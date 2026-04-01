import yaml
from pydantic import BaseModel, ValidationError, field_validator, create_model
from typing import List, Dict, Any, get_args
import os
from graphviz import Digraph
from icecream import ic

class ValidationError(Exception):
    """Custom error class to raise validation errors."""
    pass


class ValidIDStore:
    """
    This class will store static methods for validating IDs for different relationship types.
    """
    # This dictionary will store valid IDs for different relationships (e.g., Class, Tutor, Student)
    valid_ids = {}

    @staticmethod
    def add_valid_ids(relationship: str, ids: List[int]):
        """
        Adds valid IDs for a specific relationship type (e.g., Class, Tutor, Student).
        """
        ValidIDStore.valid_ids[relationship] = ids

    @staticmethod
    def create_validation_method(relationship: str):
        """
        Dynamically creates a static method for validating IDs of a specific relationship type.
        """

        def validate_id(cls, v):
            # Check if relationship exists in the valid_id store for the relationship.
            if relationship not in ValidIDStore.valid_ids:
                raise ValueError(f"No valid IDs found for relationship type: {relationship}")

            # Get the valid IDs for the relationship type
            valid_ids = ValidIDStore.valid_ids[relationship]

            invalid_ids = [item for item in v if item not in valid_ids]

            if invalid_ids:
                # Raise a validation error. This get's returned as 'e'.
                raise ValidationError(f"Invalid {relationship} ID(s): {invalid_ids}")
            
            return v

        # Return the created method
        return validate_id
    
    @staticmethod
    def get_failed_validations():
        """
        Returns the list of failed validations for retry or fixing.
        """
        return ValidIDStore.failed_validations


def get_yaml_data(file_path):
    """
    Reads and parses a YAML file, returning the data in Python dictionary format.
    
    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: Parsed data from the YAML file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If there is an error opening the file.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    try:
        # Attempt to open and read the YAML file
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    except OSError as e:
        # Handle issues with opening the file (e.g., permission errors)
        raise OSError(f"Error opening file '{file_path}': {e}")
    except yaml.YAMLError as e:
        # Handle YAML parsing errors
        raise yaml.YAMLError(f"Error parsing YAML file '{file_path}': {e}")

    return data


def create_pydantic_model(class_name: str, fields: List[Dict[str, Any]], relationships: List[Dict[str, Any]] = None, valid_ids: Dict[str, List[int]] = None):
    """
    Dynamically creates a Pydantic model class with fields and relationships, 
    and adds field validators based on relationships and valid IDs.
    
    Also creates static methods in the ValidIDStore for ID validation.
    """

    # Prepare the field annotations dictionary for the class
    annotations = {}
    
    # Handle fields in the schema
    for field in fields:
        field_name = field["name"]
        field_type = eval(field["type"])  # Convert the string 'int'/'str' into actual Python types
        annotations[field_name] = field_type

    # Handle relationships (e.g., one-to-many, many-to-one)
    if relationships:
        for relationship in relationships:
            relationship_attr = relationship["attribute"]
            relationship_type = eval(relationship["type"])
            annotations[relationship_attr] = relationship_type

    # Dynamically create the model class
    class_dict = {'__annotations__': annotations, '__module__': __name__}
    
    # Add field validators dynamically based on the relationships and valid IDs
    if relationships and valid_ids:
        for relationship in relationships:
            relationship_attr = relationship["attribute"]
            relationship_target_name = relationship["target"]  # E.g., "Class", "Tutor", "Student"

            # Check if there are valid IDs for this relationship and store them
            if relationship_attr in valid_ids:
                ValidIDStore.add_valid_ids(relationship_target_name, valid_ids[relationship_target_name])
                print(ValidIDStore.valid_ids)
                
                # Create a dynamic validation method for the relationship type
                validation_method = ValidIDStore.create_validation_method(relationship_target_name)
                
                # Dynamically add the validator as a field validator
                class_dict[f'validate_{relationship_attr}_ids'] = field_validator(relationship_attr)(validation_method)

    # Create the model class
    model = type(class_name, (BaseModel,), class_dict)
    
    return model


def parse_schema(parsed_schema, parsed_data):
    """
    Parses the given schema and data, dynamically creating models and 
    extracting valid IDs for each relationship type.

    Args:
        parsed_schema (list): List of class schemas, where each schema defines the fields and relationships.
        parsed_data (dict): Dictionary of class instances, keyed by class name.

    Returns:
        dict: A dictionary where keys are class names and values are dynamically created models.
    """
    models = {}
    valid_ids = {}  # Dictionary to store valid IDs for each relationship type

    # First pass: Create the models and extract valid IDs for each class
    for class_schema in parsed_schema:
        if isinstance(class_schema, dict):
            class_name = class_schema["name"]
            fields = class_schema.get("fields", [])
            relationships = class_schema.get("relationships", [])
            
            # Dynamically create the Pydantic model for each class
            # Extract valid IDs from the data for each class
            class_instances = parsed_data.get(class_name, [])

            if class_instances:
                # Extract valid IDs from instances for the current class
                valid_ids[class_name] = [item["id"] for item in class_instances]

            # Create the Pydantic model, passing valid IDs for validation
            models[class_name] = create_pydantic_model(class_name, fields, relationships, valid_ids)

    return models


def generate_pydantic_classes_from_yaml(yaml_file):

    classes = {}

    for item in yaml_file:
        fields = {}
        relationships = {}
        class_name = item['name']

        # Define fields
        fields = {
            field['name']: (field['type'], None) if str(field['type']).startswith('Optional') else (field['type'], ...) for field in item['fields']
        }
        if 'relationships' in item:
            relationships = {relationship['attribute']: (List[classes[relationship['target']]], ...) if relationship['schema'] == 'many_to_one' else (classes[relationship['target']], ...) for relationship in item['relationships']}
        fields.update(relationships)
        classes[class_name] = create_model(class_name, **fields)

    return classes



def generate_graphviz_schema(model_classes):
    """
    Generates a Graphviz representation of the model schema.
    """
    dot = Digraph()

    for _, cls in model_classes.items():
        dot.node(cls.__name__, cls.__name__)

    for _, cls in model_classes.items():
        for field_name, field_info in cls.__fields__.items():
            ic(cls.__fields__.items())
            if  (field_type := get_args(field_info.annotation)):
                field_type = get_args(field_info.annotation)[0]
            else:
                field_type = field_info.annotation
            if issubclass(field_type, BaseModel):
                dot.edge(cls.__name__, field_type.__name__, label=field_name)

    dot.render('output/proof_of_concept', format='png', cleanup=True)


def main():
    # File paths for the data.
    file_path_schema = 'data/model.yaml'  # The model schema YAML file
    file_path_data = 'data/data.yaml'    # Your data YAML file

    parsed_schema = get_yaml_data(file_path=file_path_schema)
    parsed_data = get_yaml_data(file_path=file_path_data)

    # Parse the schema to get the class names, attributes, and relationships
    
    models = parse_schema(parsed_schema=parsed_schema, parsed_data=parsed_data)

    generated_classes = generate_pydantic_classes_from_yaml(parsed_schema)
    generate_graphviz_schema(generated_classes)

    validated_instances = {} # To store validated instances
    invalidated_instances = {}  # To store invalidated instances

    for class_name, class_data in parsed_data.items():
        ModelClass = models[class_name]
        validated_instances[class_name] = []
        invalidated_instances[class_name] = []

        for item in class_data:
            try:
                # Attempt to create the model instance and validate
                instance = ModelClass(**item)
                validated_instances[class_name].append(instance)
            except ValidationError as e:
                print(f"Validation failed for {class_name} instance: {item}")
                print(f"Error details: {e}")
                # Store the failed instance and error in invalidated_instances
                invalidated_instances[class_name].append({"item": item, "error": str(e)})


    # Print the valid instances
    print(f"\nInstances that PASSED validation:")
    for class_name, class_instances in validated_instances.items():
        print(f"Instances for {class_name}:")
        for instance in class_instances:
            print(instance)
    
    # Print the invalid instances
    print(f"\nInstances that FAILED validation:")
    for class_name, class_instances in invalidated_instances.items():
        print(f"Instances for {class_name}:")
        for instance in class_instances:
            print(instance)


if __name__ == "__main__":
    main()

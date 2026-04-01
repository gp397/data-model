from pydantic import BaseModel, create_model, Field
from typing import Optional, List, ClassVar, Annotated, ForwardRef, get_args
from graphviz import Digraph
import yaml
import inspect
from icecream import ic

# Dynamically generate classes
def generate_pydantic_classes_from_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        model_data = yaml.safe_load(file)

    classes = {}

    for item in model_data:
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
        # print(fields)
        classes[class_name] = create_model(class_name, **fields)
        # print(classes[class_name].schema_json(indent=2))

    return classes

def generate_graphviz_schema(model_classes):
    """
    Generates a Graphviz representation of the model schema.
    """
    dot = Digraph()

    for _, cls in model_classes.items():
        # print(cls.__name__)
        dot.node(cls.__name__, cls.__name__)

    for _, cls in model_classes.items():
        ic(cls)
        for field_name, field_info in cls.__fields__.items():
            ic(cls.__fields__.items())
            if  (field_type := get_args(field_info.annotation)):
                field_type = get_args(field_info.annotation)[0]
                # print(get_args(field_info.annotation)[0])
            else:
                field_type = field_info.annotation
                # print(field_info.annotation)
            if issubclass(field_type, BaseModel):
                # print(cls.__name__ + " : ", field_name)
                dot.edge(cls.__name__, field_type.__name__, label=field_name)

    dot.render('output/test5', format='png', cleanup=True)



# ??
def import_data_from_yaml(yaml_file, generated_classes):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    objects = {}
    for class_name, items in data.items():
        class_type = generated_classes[class_name]
        objects[class_name] = [class_type(**item) for item in items]
    
    return objects

# Load model
model_yaml_file = 'data/test5_model.yaml'
generated_classes = generate_pydantic_classes_from_yaml(model_yaml_file)

ic(generated_classes)
# Print model schema example
# print(generated_classes['Comment'].schema_json(indent=2))

generate_graphviz_schema(generated_classes)

# Load data
data_yaml_file = 'data/test5_data.yaml'
#sample_data = import_data_from_yaml(data_yaml_file, generated_classes)
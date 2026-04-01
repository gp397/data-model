import yaml
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Set
#from icecream import ic

"""
What Pydantic DOES Check Automatically:
    Data Types: Pydantic will check that the data provided matches expected types (e.g., strings, integers, lists).
    Field Existence: It ensures required fields are present.
    Value Constraints: You can set additional constraints like string length, range conditions for numbers, regex patterns for strings, etc.

What Pydantic DOES NOT Check Automatically:
    Referential Integrity: Checking if IDs correspond to valid or existing records (like a class ID actually existing in your class data set).
    Contextual Validation: Ensuring that data makes sense within your application's context (such as a tutor's ID not being in a list of class IDs).
"""

def load_yaml_file(filepath):
    """
    Load YAML data from a file and return the data as a Python variable.
    Deserialisation: This is a process of converting a YAML object into a usable Python object. This is what yaml.safe_load does.

    Args:
    filepath (str): The path to the YAML file to be loaded.

    Returns:
    object: The Python representation of the YAML data, typically a dictionary or list.
    """
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print("The file was not found.")
    except yaml.YAMLError as exc:
        print(f"An error occurred while parsing YAML file: {exc}")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


def check_class_id_exists(items, valid_class_ids):
    for item in items:
        if item not in valid_class_ids:
            raise ValueError(f"Creation Error: Invalid class ID: {item}")


class ValidClassIDStore:
    _instance = None
    valid_class_ids = set()

    @staticmethod
    def get_instance():
        if ValidClassIDStore._instance is None:
            ValidClassIDStore._instance = ValidClassIDStore()
        return ValidClassIDStore._instance

    @classmethod
    def add_class_id(cls, class_id):
        cls.get_instance().valid_class_ids.add(class_id)

    @classmethod
    def check_and_add_class_id(cls, class_id):
        if class_id not in cls.get_instance().valid_class_ids:
            cls.add_class_id(class_id)
            return False  # Indicating the ID was not previously present and has been added
        return True  # Indicating the ID was already present


class Class(BaseModel):
    name: str
    class_id: str  # Primary key or unique identifier for the class

    # Using a validator to ensure the classes variable contains only valid Class IDs
    @field_validator('class_id')
    @classmethod
    def check_and_add_class_id(cls, v):
        if not ValidClassIDStore.check_and_add_class_id(v):
            pass
        return v


class Tutor(BaseModel):
    name: str
    employee_id: str
    valid_class_ids: Set[str] = Field(default_factory=set)
    classes: Optional[List[str]] = Field(default_factory=list)  # List of class IDs the tutor teaches
        
    # Using a validator to ensure the classes variable contains only valid Class IDs
    @field_validator('classes')
    @classmethod
    def check_class_id_exists(cls, v):
        print(valid_class_ids)
        check_class_id_exists(items=v, valid_class_ids=valid_class_ids)
        return v


class Student(BaseModel):
    name: str
    student_id: str
    classes: Optional[List[str]] = None  # List of class IDs the student attends

    # Using a validator to ensure the classes variable contains only valid Class IDs
    @field_validator('classes')
    @classmethod
    def check_class_id_exists(cls, v):
        check_class_id_exists(items=v, valid_class_ids=valid_class_ids)
        return v


def fetch_valid_class_ids():
    valid_class_ids = {"id_c1"}
    for id in valid_class_ids:
        if not ValidClassIDStore.check_and_add_class_id(id):
            pass
    #return ValidClassIDStore.valid_class_ids # Replace this function with a fetch froma  file or database

def fetch_valid_tutor_ids():
    return {"id_t1", "id_t2"} # Replace this function with a fetch from a file or database

def fetch_valid_student_ids():
    return {"id_s1", "id_s2", "id_s3", "id_s4", "id_s5"} # Replace this function with a fetch from a file or database


if __name__ == "__main__":
    
    model_path = "data/test3_model.yaml"
    data_path = "data/test3_data.yaml"

    #model_data = load_yaml_file(model_path) # Redundant code.
    data = load_yaml_file(data_path)

    # Simluates getting data from a database or static file.
    valid_class_ids = fetch_valid_class_ids()
    valid_tutor_ids = fetch_valid_tutor_ids()
    valid_student_ids = fetch_valid_student_ids()

    if data is not None:
        classes = [Class(**cls) for cls in data.get('classes', [])]
        valid_class_ids = ValidClassIDStore.valid_class_ids
        
        tutors = [Tutor(**tutor, valid_class_ids=valid_class_ids) for tutor in data.get('tutors', [])]
        students = [Student(**student, valid_class_ids=valid_class_ids) for student in data.get('students', [])]

        for cls in classes:
            print(cls)
        for tutor in tutors:
            print(tutor)
        for student in students:
            print(student)
    else:
        print("No valid data to process.")


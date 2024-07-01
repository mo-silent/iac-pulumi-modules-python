# The following two lines of code are used by model developers for testing
import sys
sys.path.append("../../..") 

# When creating a resource using this model, ignore the above two lines of code
import importlib
import pulumi
# The lib is from https://github.com/mo-silent/iac-pulumi-modules-python.git
from iac_modules.utils.common import Common


STACKNAME = pulumi.get_stack()


def execute_modules(data, current_stack, key,  tags =  None, assume_role = None, depends_resources = None):
    try:
        # import the module
        module = importlib.import_module("iac_modules.alicloud." + key)
        print("import modules: " + module.__name__)
        # get the function
        function = getattr(module, key.upper())
        outputs = []
        results = []
        for v  in data:
            # print(v)
            # if key != "rg":
            #     v["rg_id"]["rg_id"] = Common.get_rg_id(v.get("rg_id"), current_stack)
            # run function
            if v.get("enabled"):
                res = function(v, current_stack, tags, assume_role, depends_resources)
                results.append(res) 
                outputs.append(res.outputs)
        # define the pulumi outputs
        pulumi.export(key+"_outputs", outputs)
        return results
    except Exception as e:
        print(f"Error creating {key}: {e}")
        return None

def main_program(values_data):
  """
  Main program
  """
  # rg_id = None
  resources_data = values_data.get("resources")
  tags = values_data.get("global").get("variables").get("tags")

  # define alicloud assume role
  assume_role = values_data.get("global").get("variables").get("assume_role")
  # If you want to not use assume role, you can set assume_role to None
  # assume_role = alicloud.ProviderAssumeRoleArgs(role_arn=assume_role_data.get("role_arn"), session_name=assume_role_data.get("session_name"))

  # Create ResourceGroup
  key = "rg"
  rg = execute_modules(resources_data.get(key), STACKNAME, key, tags, assume_role)
  key = "oss"
  oss = execute_modules(resources_data.get(key), STACKNAME, key, tags, assume_role, depends_resources={"rg": rg})


 


if __name__ == "__main__":
  try:
    values_data = Common.load_config("resources." + STACKNAME +".yaml")
  except Exception as e:
    print(f"Error loading resources.{STACKNAME}.yaml file: {e}")
    sys.exit(1)
  # run the pulumi program
  main_program(values_data)
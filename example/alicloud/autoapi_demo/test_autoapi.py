# -*- coding: utf-8 -*-
import sys

sys.path.append("../../..")

import pulumi
import yaml
import pulumi.automation as auto
from iac_modules.alicloud.resource_group import ResourceGroup
from iac_modules.alicloud.vpc import VPC

stack_name="qa"
project_name="aliyun-test"

# define provider version
OPTS = pulumi.ResourceOptions(version="3.55.1")


def stack_init():
  ws = auto.LocalWorkspace(project_settings=auto.ProjectSettings(
    name=project_name,
    runtime="python",
          # backend=auto.ProjectBackend(url="https://app.pulumi.com/mo-silent"), # default is app.pulumi.com, not need to set.
  ))
  # ws.install_plugin("aws", "v4.0.0")
  try:
    stack = ws.create_stack(stack_name=stack_name)
  except Exception as e:
    print(f"Stack '{stack_name}' already exists or an error occurred: {e}")
    stack = auto.Stack.select(stack_name=stack_name, workspace=ws)
  return stack
def on_output(event):
    print(event)

def load_config(file_name):
  """
  Load configuration from a file
  """
  with open(file_name,'r') as values:
    values_data=yaml.load(values,Loader=yaml.FullLoader)
  return values_data

def pulumi_program(values_data):
  """
  Main program
  """
  rg = None
  outputs = {}
  resources_data = values_data.get("resources")
  global_variables = values_data.get("global").get("variables")

  # Determine whether to create ResourceGroup
  if resources_data.get("rg").get("enabled"):
    rg_name = "%s-%s-%s-%s-%s" % (global_variables.get("bu"),global_variables.get("env"),global_variables.get("rack_zone"),global_variables.get("project"),resources_data.get("rg").get("name"))
    # Create ResourceGroup
    rg = ResourceGroup(rg_name, resource_group_name=rg_name, opts=OPTS)
    # Merge the output into a list
    rg_outputs = [rg.output]
    # add the resources outputs to the pulumi outputs
    outputs.update({"rg_outputs": rg_outputs})
  vpc_data = resources_data.get("vpc")
  for vd in vpc_data:
    vpc_outputs = []
    if vd.get("enabled"):
      vpc_name = "%s-%s-%s-%s-%s" % (global_variables.get("bu"),global_variables.get("env"),global_variables.get("rack_zone"),global_variables.get("project"), vd.get("name"))
      vpc = VPC(rg.rg.id, vpc_name, vpc_name, cidr_block=vd.get("cidr_block"), dry_run=vd.get("dry_run"),opts=OPTS)
      # Merge the output into a list
      vpc_outputs.append(vpc.output)
    # add the resources outputs to the pulumi outputs
    outputs.update({"vpc_outputs": vpc_outputs})
  # pulumi.export("outputs", outputs)
  return outputs

# ApiProgram class is used to run the pulumi_program
class ApiProgram:
  """
  ApiProgram class
  """
  def __init__(self, values_data):
    self.values_data = values_data

  def run(self):
    pulumi_program(self.values_data)

if __name__ == "__main__":
  values_data = load_config("values.yaml")
  stack = stack_init()
  # init automatic api program
  iac_program = ApiProgram(values_data)
  # the workspace program can't use functions with arguments
  stack.workspace.program=iac_program.run
  pre_res = stack.preview(on_output=on_output)

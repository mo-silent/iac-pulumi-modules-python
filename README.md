# pulumi-alicloud-modules
Pulumi modules as package for alicloud resources

# Installing

## Python

### Create github token

Open your github `Settings` page and click `developer setting` on the left TAB. On the `developer setting` page, select `Personal access token`, click `G`eneral new token`, and select `classic`.

### use github token to install modules
To use from Python, install using `pip`:
```python
pip install git+https://github.com/mo-silent/iac-pulumi-modules-python.git

# you can use history version, example:
pip install git+https://github.com/mo-silent/iac-pulumi-modules-python.git@v0.0.1-beta
```

# Specification
See [specification.md](./specification.md)


# Examples

## Environment variable setting

### Linux
Modify the `~/.bashrc` file by adding the following at the end of the file
```bash
# alicloud aksk
export ALICLOUD_ACCESS_KEY="Your alicloud access key" 
export ALICLOUD_SECRET_KEY="Your alicloud secret key" 
# aruze sa access key
export AZURE_STORAGE_ACCOUNT='Your azure blob sa name'
export AZURE_STORAGE_KEY='Your azure blob sa access key'
```

## Python

This is a python example to use the project.
Before run this example, you need to install the project. Please refer to the installation section.

### Use Pulumi ClI

Alicloud Example Directory structure

```bash
.
├── resources.qa.yaml # resources.<stack>.yaml, the resources configure
├── Pulumi.yaml # Pulumi.yaml must configure if use pulumi cli.
├── __main__.py # Pulumi cli must configure __main__.py
```

resources.<stack>.yaml
```yaml
global:
  backend: 
    enabled: false
  variables:
    bu: "sanbox"
    shourt_bu: "dps"
    env: "qa"
    project: "cloud"
    assume_role:
      role_arn: acs:ram::1521538100145635:role/aliyunresourceadmin
      session_name: "pulumi-test"
    tags:
      Bu: "sanbox"
      Environment: "qa"
resources:
  rg:
    - name: "sanbox-qa-cnsh-cloud-pulumi-rg-0"
      enabled: true
    - name: "sanbox-qa-cnsh-cloud-pulumi-rg-1"
      enabled: true
  oss:
    - name: "sanbox-qa-cnsh-cloud-pulumi-oss-0"
      rg_id:
        depends_on: null #stack name. If current stack, set null
        name: 
          - sanbox-qa-cnsh-cloud-pulumi-rg-0 # depends resources value
      enabled: false
      region: cn-shanghai
      version: 3.55.1
      bucket: "sanbox-qa-cnsh-cloud-pulumi-oss-0"
      storage_class: Standard # [Standard(default),IA,Archive,ColdArchive,DeepColdArchive]
      force_destroy: false
      lifecycle_rule_allow_same_action_overlap: false
      # ignore_changes
      ignore_changes:
        - tags
      # block
      access_monitor:
        enabled: true
        status: "Enabled"
      cors_rules:
        enabled: false
        cors_rules:
          - allowed_menthods: ["GET"] # ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
            allowed_origins: ["*"]
            allowed_headers: ["*"]
            expose_headers: null
            max_age_seconds: 300
      lifecycle_rules:
        enabled: false
        lifecycle_rules:
          - enabled: true
            prefix: "test/"
            tags: null
            expirations:
              enabled: true
              expirations:
                - date: null
                  days: 1
                  create_before_date: null
                  expiration_date: null
      server_side_encryption_rule:
        enabled: true
        sse_algorithm: "AES256"
        kms_master_key_id: null
      transfer_acceleration:
        enabled: true
      versioning:
        enabled: true
        status: "Enabled"
      # sub resources
      subresource:
        acl: 
          - enabled: true
            acl: "private"
        https_config:
          - enabled: true
            enable: true
            tls_versions: ["TLSv1.2","TLSv1.3"]
        policy:
          - enabled: true
            policy_file: null # policy file is required when policy is null
            policy: |
              {
                "Version": "1",
                "Statement": [
                  {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "oss:GetObject",
                    "Resource": "acs:oss:*:*:*/*"
                  }
                ]
              }
    - name: "sanbox-qa-cnsh-cloud-pulumi-oss-1"
      rg_id:
        depends_on: null #stack name. If current stack, set null
        name: 
          - sanbox-qa-cnsh-cloud-pulumi-rg-1 # depends resources value
        # rg_id: null # Placeholders that users do not need to fill in
      enabled: true
      region: cn-shanghai
      version: 3.55.1
      bucket: "sanbox-qa-cnsh-cloud-pulumi-oss-1"
      storage_class: Standard # [Standard(default),IA,Archive,ColdArchive,DeepColdArchive]
      force_destroy: false
      lifecycle_rule_allow_same_action_overlap: false
      # block
      access_monitor:
        enabled: true
        status: "Enabled"
      cors_rules:
        enabled: false
        cors_rules:
          - allowed_menthods: ["GET"] # ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
            allowed_origins: ["*"]
            allowed_headers: ["*"]
            expose_headers: null
            max_age_seconds: 300
      lifecycle_rules:
        enabled: true
        lifecycle_rules:
          - enabled: true
            prefix: "test/"
            tags: null
            expirations:
              enabled: true
              expirations:
                - date: null
                  days: 1
                  create_before_date: null
                  expired_object_delete_marker: null
          - enabled: false
            prefix: null
            tags: null
            expirations:
              enabled: true
              expirations:
                - date: null
                  days: 5
                  create_before_date: null
                  expired_object_delete_marker: null
      server_side_encryption_rule:
        enabled: true
        sse_algorithm: "AES256"
        kms_master_key_id: null
      transfer_acceleration:
        enabled: true
      versioning:
        enabled: true
        status: "Enabled"
      # sub resources
      subresource:
        acl: 
          - enabled: true
            acl: "private"
        https_config:
          - enabled: true
            enable: true
            tls_versions: ["TLSv1.2","TLSv1.3"]
        policy:
          - enabled: true
            policy_file: tran-qa-cnsh-cloud-oss-1.json # policy file is required when policy is null
            policy: null 
```

\_\_main\_\_.py*

```python
# The following two lines of code are used by model developers for testing
import sys
sys.path.append("..") 

# When creating a resource using this model, ignore the above two lines of code
import yaml
import importlib
import pulumi
import pulumi_alicloud as alicloud
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
  oss = execute_modules(resources_data.get(key), STACKNAME, key, tags, assume_role, depends_resources=rg)



if __name__ == "__main__":
  try:
    values_data = Common.load_config("resources." + STACKNAME +".yaml")
  except Exception as e:
    print(f"Error loading resources.{STACKNAME}.yaml file: {e}")
    sys.exit(1)
  # run the pulumi program
  main_program(values_data)
```

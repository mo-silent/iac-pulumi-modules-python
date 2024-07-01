#coding:utf-8
#!/usr/bin/env python3
import pulumi_alicloud as alicloud
import pulumi
from iac_modules.utils.common import StackUtils

class RG:

    # name is deprecated from provider version 1.114.0
    def __init__(self, data, current_stack, tags =  None, assume_role = None, depends_resources = None):
        self.tags = tags
        self.data = data
        self.current_stack = current_stack
        self.assume_role = assume_role
        self.provider = StackUtils.get_provider(self.data.get("name"), self.data.get("region"), self.assume_role, self.data.get("version"))
        self.depends_resources = depends_resources
        self.outputs = {}
        self.rg = self.resource_rg()

    def format_data(self):
        self.resource_name = self.data.get("name")
        self.resource_group_name=self.resource_name
        if self.data.get("display_name") is None:
            self.display_name=self.resource_name
        else:
            self.display_name=self.data.get("display_name")
        self.opts = pulumi.ResourceOptions(provider=self.provider)

    def resource_rg(self):
        self.format_data()
        rg=alicloud.resourcemanager.ResourceGroup(
            tags=self.tags,
            resource_name=self.resource_name,
            resource_group_name=self.resource_group_name,
            display_name=self.display_name,
            opts=self.opts
        )
        output ={ "rg" : {
            "rg_id": rg.id,
            "rg_name": self.resource_group_name,
            "rg_status": rg.status,
            "account_id": rg.account_id,
            }
        }
        self.outputs.update(output)
        return rg

#coding:utf-8
#!/usr/bin/env python3
import pulumi_alicloud as alicloud
import pulumi
import json
from iac_modules.utils.common import StackUtils, Common

class OSS:

    # name is deprecated from provider version 1.114.0
    def __init__(self, data, current_stack, tags =  None, assume_role = None, depends_resources = None):
        # self.rg_id = self.data.get("rg_id").get("rg_id")
        self.tags = tags
        self.data = data
        self.current_stack = current_stack
        self.assume_role = assume_role
        # self.stack = StackUtils.get_depends_stack().name
        self.provider = StackUtils.get_provider(self.data.get("name"), self.data.get("region"), self.assume_role, self.data.get("version"))
        self.depends_resources = depends_resources
        self.outputs = {}
        # create main resource
        self.oss = self.resource_oss()
        # create_subresource
        self.associate_subresource(self.data.get("subresource"))
    
    def format_data(self):
        self.resource_name = self.data.get("name")
        if self.data.get("bucket") == None:
            self.bucket = self.data.get("name")
        else:
            self.bucket = self.data.get("bucket")
        self.depends_on, self.rg_id = Common.get_rg_depends(self.data.get("rg_id"), self.depends_resources.get("rg"))
        self.storage_class = self.data.get("storage_class")
        self.force_destroy = self.data.get("force_destroy")
        self.lifecycle_rule_allow_same_action_overlap = self.data.get("lifecycle_rule_allow_same_action_overlap")
        # format object data
        self.redundancy_type =self.format_redundancy_type(self.data.get("redundancy_type"), self.current_stack) 
        self.access_monitor = self.format_access_monitor(access_monitor=self.data.get("access_monitor"))
        self.cors_rules = self.format_cors_rules(cors_rules=self.data.get("cors_rules"))
        self.lifecycle_rules = self.format_lifecycle_rules(lifecycle_rules=self.data.get("lifecycle_rules"))
        if self.lifecycle_rules == None or len(self.lifecycle_rules) > 1 :
            self.lifecycle_rule_allow_same_action_overlap = True
        self.server_side_encryption_rule = self.format_server_side_encryption_rule(server_side_encryption_rule=self.data.get("server_side_encryption_rule"))
        self.transfer_acceleration = self.format_transfer_acceleration(transfer_acceleration=self.data.get("transfer_acceleration"))
        self.versioning = self.format_versioning(versioning=self.data.get("versioning"))
        self.website = self.format_website(website=self.data.get("website"))
        self.logging = self.format_logging(logging=self.data.get("logging"))
        self.opts = pulumi.ResourceOptions(provider=self.provider, depends_on=self.depends_on)
    
    def resource_oss(self):
        self.format_data()
        oss=alicloud.oss.Bucket(
            tags=self.tags,resource_group_id=self.rg_id,resource_name=self.resource_name,
            bucket=self.bucket,access_monitor=self.access_monitor,cors_rules=self.cors_rules,
            force_destroy=self.force_destroy,lifecycle_rule_allow_same_action_overlap=self.lifecycle_rule_allow_same_action_overlap,
            lifecycle_rules=self.lifecycle_rules,logging=self.logging,redundancy_type=self.redundancy_type,
            server_side_encryption_rule=self.server_side_encryption_rule,storage_class=self.storage_class,
            transfer_acceleration=self.transfer_acceleration,versioning=self.versioning,website=self.website,
            opts=self.opts,
        )
        output = {"oss":{
            "oss_id": oss.id,
            "oss_name": self.resource_name,
            "oss_creation_date": oss.creation_date,
            "oss_extranet_endpoint": oss.extranet_endpoint,
            "oss_intranet_endpoint": oss.intranet_endpoint,
            "oss_location": oss.location,
            "oss_owner": oss.owner,
        }}
        self.outputs.update(output)
        return oss
  
    def associate_acl(self, data):
        oss_acl = alicloud.oss.BucketAcl(resource_name=self.resource_name, acl=data.get("acl"), bucket=self.oss.bucket, opts=self.opts)
        output = { "oss_acl": {
            "id": oss_acl.id,
            }
        }
        self.outputs.update(output)
        return oss_acl
  
    def associate_https_config(self, data):
        oss_https_config = alicloud.oss.BucketHttpsConfig(resource_name=self.resource_name, bucket=self.oss.bucket, enable=data.get("enable"), tls_versions=data.get("tls_versions"), opts=self.opts)
        output = { "oss_https_config": {
            "id": oss_https_config.id,
            }
        }
        self.outputs.update(output)
        return oss_https_config
  
    def associate_policy(self, data):
        policy = data.get("policy")
        if policy == None:
            with open(data.get("policy_file"), "r") as f:
                policy = json.load(f)
                policy = json.dumps(policy)
        oss_policy = alicloud.oss.BucketPolicy(resource_name=self.resource_name, bucket=self.oss.bucket, policy=policy, opts=self.opts)
        output = { "oss_policy": {
            "id": oss_policy.id,
        }
        }
        self.outputs.update(output)
        return oss_policy
  
    def associate_subresource(self, sub_data):
        default_acl = {"acl": "private"}
        default_https_config = {"enable": True, "tls_versions":["TLSv1.2","TLSv1.3"]}
        if sub_data == None:
            self.associate_acl(default_acl)
            self.associate_https_config(default_https_config)
            return
        # associate acl
        if sub_data.get("acl") != None:
            for v in sub_data.get("acl"):
                if not v.get("enabled"):
                    v["acl"] == "private"
                self.associate_acl(v)
        else:
            self.associate_acl(default_acl)
        # associate https config
        if sub_data.get("https_config") != None:
            for v in sub_data.get("https_config"):
                if not v.get("enable"):
                    v["enable"] = True
                    v["tls_versions"] = ["TLSv1.2","TLSv1.3"]
                self.associate_https_config(v)
        else:
            self.associate_https_config(default_https_config)
        # associate policy
        if sub_data.get("policy") != None:
            for v in sub_data.get("policy"):
                self.associate_policy(v)

    @staticmethod
    def format_redundancy_type(redundancy_type, current_stack):
        if redundancy_type == None:
            return "ZRS" if current_stack == "prd" else "LRS"
        return redundancy_type

    @staticmethod
    def format_access_monitor(access_monitor):
        if access_monitor != None and access_monitor.get("enabled"):
            return alicloud.oss.BucketAccessMonitorArgs(status=access_monitor.get("status"))
        return None

    @staticmethod
    def format_cors_rules(cors_rules):
        data = None
        if cors_rules != None and cors_rules.get("enabled"):
            data = []
            for v in cors_rules.get("cors_rules"):
                data.append(alicloud.oss.BucketCorsRuleArgs(allowed_menthods=v.get("allowed_menthods"),allowed_headers=v.get("allowed_headers"),allowed_origins=v.get("allowed_origins"),expose_headers=v.get("expose_headers"),max_age_seconds=v.get("max_age_seconds")))
        return data

    @staticmethod
    def format_lifecycle_rules(lifecycle_rules):
        data = None
        if lifecycle_rules != None and lifecycle_rules.get("enabled"):
            data = []
            for v in lifecycle_rules.get("lifecycle_rules"):
                expirations_data = None
                if v.get("expirations").get("enabled"):
                    expirations_data = []
                    for e in v.get("expirations").get("expirations"):
                        expirations_data.append(alicloud.oss.BucketLifecycleRuleExpirationArgs(created_before_date=e.get("create_before_date"),days=e.get("days"),date=e.get("date"),expired_object_delete_marker=e.get("expired_object_delete_marker")))
                data.append(alicloud.oss.BucketLifecycleRuleArgs(enabled=v.get("enabled"),prefix=v.get("prefix"),tags=v.get("tags"),expirations=expirations_data))
        return data

    @staticmethod
    def format_server_side_encryption_rule(server_side_encryption_rule):
        if server_side_encryption_rule != None and server_side_encryption_rule.get("enabled"):
            return alicloud.oss.BucketServerSideEncryptionRuleArgs(sse_algorithm=server_side_encryption_rule.get("sse_algorithm"),kms_master_key_id=server_side_encryption_rule.get("kms_master_key_id"))
        return None

    @staticmethod
    def format_transfer_acceleration(transfer_acceleration):
        if transfer_acceleration != None and transfer_acceleration.get("enabled"):
            return alicloud.oss.BucketTransferAccelerationArgs(enabled=transfer_acceleration.get("enabled"))
        return None
  
    @staticmethod
    def format_versioning(versioning):
        if versioning != None and versioning.get("enabled"):
            return alicloud.oss.BucketVersioningArgs(status=versioning.get("status"))
        return None
  
    @staticmethod
    def format_website(website):
        if website != None and website.get("enabled"):
            return alicloud.oss.BucketWebsiteArgs(index_document=website.get("index_document"), error_document=website.get("error_document"))
        return None
  
    @staticmethod
    def format_logging(logging):
        if logging != None and logging.get("enabled"):
            return alicloud.oss.BucketLoggingArgs(target_bucket=logging.get("target_bucket"), target_prefix=logging.get("target_prefix"))
        return None
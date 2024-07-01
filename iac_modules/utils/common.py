#coding:utf-8
#!/usr/bin/env python3
"""
-------------------------------------------------
   File Name:     common.py
   Description : 
   Author :        silent.mo
   date:          2024/06/14
   Copyright:      (c) P&G
-------------------------------------------------
   Change Activity:
                   2024/06/20: update by silent.mo, Modify packega name
-------------------------------------------------
"""

import pulumi
import yaml
import pulumi_alicloud as alicloud

class StackUtils():
    def __init__(self) -> None:
        pass
    
    # get_depends_on function is get the current stack resource interdependence information
    @staticmethod
    def get_depends_on(depends_resources, depends_names, resource_name, attr):
        resource = []
        outputs = []
        for v in depends_resources:
            for dn in depends_names:
                if dn == v.outputs.get(resource_name).get(attr):
                    resource.append(getattr(v, resource_name))
                    outputs.append(v.outputs)
        return resource, outputs

    # get_depends_stack function is get the current stack resource depends on other stacks
    @staticmethod
    def get_depends_stack(name: str = None) -> pulumi.StackReference:
        # if name == None:
        #     name = pulumi.get_stack()
        return pulumi.StackReference(name=name)
    
    # get_depends_output function is get the current stack resource depends on other stacks output, cann't get current stack output. 
    @staticmethod
    def get_depends_output(depends_name, stack: pulumi.StackReference = None):
        if stack.name == None:
            return []
        return stack.get_output(depends_name)
    
    @staticmethod
    def get_provider(name, region, assume_role, version):
        return alicloud.Provider(name, region=region, assume_role=assume_role, opts=pulumi.ResourceOptions(version=version))



class Common():
    def __init__(self) -> None:
       pass


    @ staticmethod
    def load_config(file_name):
        """
        Load configuration from a file
        """
        with open(file_name,'r') as values:
            values_data=yaml.load(values,Loader=yaml.FullLoader)
        return values_data

    @staticmethod
    # Define a function to get a specific rg_id
    def get_specific_rg_id(result, depends_names):
        rg_id = None
        for rg in result:
            # print(rg)
            for rn in depends_names:
                if rg.get("rg").get("rg_name") == rn:
                    rg_id = rg.get("rg").get("rg_id")
        return rg_id
    
    @ staticmethod
    def get_rg_depends(rg_data, depends_resources):
        stack_name = rg_data.get("depends_on")
        depends_names = rg_data.get("name")
        rg = None
        rg_id = None
        print(stack_name)
        print(depends_names)
        if stack_name == None:
            rg, rg_output = StackUtils.get_depends_on(depends_resources, depends_names, "rg", "rg_name")
            rg_id = Common.get_specific_rg_id(rg_output, depends_names)
            # print(f"The {depends_names} rg_id is: {rg_id}")
        else:
            print(stack_name)
            try:
                stack = StackUtils.get_depends_stack(stack_name)
                rg_output = StackUtils.get_depends_output("rg_outputs", stack)
                # print rg_id
                rg_output.apply(lambda result: print(f"The depends stack is: {stack_name} and depends Resources Group {depends_names} id is: {Common.get_specific_rg_id(result, depends_names)}"))
                rg_id = rg_output.apply(lambda result: Common.get_specific_rg_id(result, depends_names))
            except Exception as e:
                print(f"Error obtaining stack: {stack_name} dependency, error: {e}")
        # print(rg_id)
        
        return rg, rg_id

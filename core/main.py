#!/usr/bin/python3
import lib.scenario_helper as scenario_helper
import lib.vagrant_helper as vagrant_helper
import lib.ansible_helper as ansible_helper
import os
import click
from prettytable import PrettyTable

@click.group()
def VulnNetGen():
    pass

def get_scenario_list():
    directory = "../scenarios"
    return [name for name in os.listdir(directory) if os.path.isdir(directory+'/'+name)]

@VulnNetGen.command("list")
def list_scenerios():
    """List out all the available scenerios"""
    scenarios_list = get_scenario_list()
    table = PrettyTable(["Scenerios"])
    for scenario in scenarios_list:
        table.add_row([scenario])
    table.align = "l"
    print(table)

def validate_scenario(ctx, param, value):
    scenarios_list = get_scenario_list()
    if not value in scenarios_list:
        raise click.BadParameter('Invalid scenario name!')
    return value

@VulnNetGen.command("run")
@click.option("-s", "--scenario", "scenario", 
              default='linux_default_ftp', show_default='linux_default_ftp',
              required=True, prompt='Please enter the scenario',
              callback=validate_scenario)
def run_scenarios(scenario):
    """Running the specified scenerios"""    
    scenario_helper.create_scenario(scenario)
    
if __name__ == "__main__":
    VulnNetGen()
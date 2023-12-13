import lib.scenario_helper as scenario_helper
import lib.vagrant_helper as vagrant_helper
import lib.ansible_helper as ansible_helper

def main():
    scenario_helper.create_scenario("linux_default_ftp")
    
main()
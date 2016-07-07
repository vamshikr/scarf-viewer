import json
import os.path as osp
import sys
import xml.etree.ElementTree as xet


def scarf_to_json(xml_filepath, extra_attr):
    '''Returns json, and fileset (SourceFiles)'''
    
    tree = xet.ElementTree(file=xml_filepath)
    root = tree.getroot()

    tool_type = root.attrib['tool_name']
    tool_ver = root.attrib['tool_version']
    
    json_dict = dict()
    json_dict.update({'tool-type': tool_type,
                      'tool-version': tool_ver})
    json_dict.update(extra_attr)
    bug_instances = []

    str_to_bool = lambda _str: True if _str == "true" else False
    source_files = set()
    
    for bug in root.iter('BugInstance'):
        bug_dict = {'id': int(bug.get('id'))}
        # print(bug_dict, flush=True)
        
        if bug.find('ClassName') is not None:
            bug_dict['ClassName'] = bug.find('ClassName').text

        if bug.find('Methods') is not None:
            bug_dict['Methods'] = []
            
            for method in bug.find('Methods').iter('Method'):
                method_dict = {'id': int(method.get('id')),
                               'primary': str_to_bool(method.get('primary'))}
                method_dict['name'] = method.text
                bug_dict['Methods'].append(method_dict)

        if bug.find('BugLocations') is not None:
            bug_dict['BugLocations'] = []
            
            for location in bug.find('BugLocations').iter('Location'):
                loc_dict = {'id': int(location.get('id')),
                            'primary': str_to_bool(location.get('primary'))}
                loc_dict['SourceFile'] = location.find('SourceFile').text
                source_files.add(loc_dict['SourceFile'])
                
                if location.find('StartLine') is not None:
                    loc_dict['StartLine'] = int(location.find('StartLine').text)
                if location.find('EndLine') is not None:
                    loc_dict['EndLine'] = int(location.find('EndLine').text)
                if location.find('Explanation') is not None:
                    loc_dict['Explanation'] = location.find('Explanation').text
                bug_dict['BugLocations'].append(loc_dict)

        if bug.find('BugGroup') is not None:
            bug_dict['BugGroup'] = bug.find('BugGroup').text

        if bug.find('BugRank') is not None:
            bug_dict['BugRank'] = bug.find('BugRank').text

        bug_dict['BugCode'] = bug.find('BugCode').text
        #bug_dict['CWEID'] = cwe_mapping[tool_type].get(bug_dict['BugCode'], None)
        bug_dict['CweId'] = bug.find('CweId').text if bug.find('CweId') is not None else None

        if bug.find('BugSeverity') is not None:
            bug_dict['BugSeverity'] = bug.find('BugSeverity').text

        bug_dict['BugMessage'] = bug.find('BugMessage').text

        bug_instances.append(bug_dict)
        
    json_dict['BugInstances'] = bug_instances

    return (json_dict, source_files)


def scarf_to_json_file(xml_filepath, extra_attr, json_filepath=None):

    if json_filepath is None:
        json_filepath = osp.join(osp.dirname(xml_filepath),
                                 osp.splitext(xml_filepath)[0] + '.json')

    if osp.isfile(json_filepath):
        raise FileExistsError(json_filepath)

    json_dict, _ = scarf_to_json(xml_filepath, extra_attr)
        
    with open(json_filepath, 'w') as json_fp:
        json.dump(json_dict, json_fp)

    return json_filepath
        

def main(args):
    scarf_to_json_file(args[1], {'package-short-name': 'hadoop',
                                 'package-version': '1.1.2',
                                 'platform': 'rhel-6.4-64',
                                 'assessment-date': 'Sun Apr 10 23:18:08 CDT 2016'})

if __name__ == '__main__':
    main(sys.argv)

from sceptre.resolvers import Resolver
import json
import os
import subprocess


class OnePasswordResolver(Resolver):
    def __init__(self, *args, **kwargs):
        super(OnePasswordResolver, self).__init__(*args, **kwargs)
        op_config_file = os.path.join(os.environ['HOME'], '.op', 'config')
        if os.path.isfile(op_config_file):
            with open(op_config_file, 'r') as conf:
                self.op_config = json.load(conf)

        else:
            raise FileNotFoundError(
                "The file {} was not found. ".format(op_config_file) +
                "Set up the 1password CLI before using this resolver. " +
                "https://1password.com/downloads/command-line/"
            )


    def resolve(self):
        """
        Attempts to get the 1password secret named by ``param``
        :param param: The name of the 1password secret in which to return.
        :type param: str
        :returns: 1password secret value.
        :rtype: str
        :raises: KeyError
        """

        param_data = self.argument.split("#")
        search_field = param_data[0]
        if len(param_data) > 1:
            tags = self.argument.split("#")[1].split(",")
        else:
            tags = []

        items = json.loads(subprocess.check_output(['op','list','items']))
        filtered = [
            item for item in items
            if all(tag in item['overview']['tags'] for tag in tags)
        ]
        if len(filtered) > 1:
            raise ValueError("Query for tags {} returned more than one result in 1password: {}".format(
                tags, ["Vault: {}, UUID: {}, Title: {}".format(
                    item['vaultUuid'], item['uuid'], item['overview']['title'])
                    for item in filtered]
            ))
        elif len(filtered) == 0:
            raise ValueError("Query for tags {} returned no results in 1password.".format(tags))
        else:
            uuid = filtered[0]['uuid']
            data = json.loads(subprocess.check_output(['op','get','item', uuid]))
            # need different api calls for doc / vs secret?
            if search_field == 'document':
                if 'documentAttributes' not in data['details'].keys():
                    raise ValueError("Secret {} is not a document.".format(search_field, data['overview']['title']))
                else:
                    return subprocess.check_output(['op','get','document', data['uuid']])
            else:
                field_data = [
                    field['value'] for field in data['details']['fields']
                    if field['designation'] == search_field
                ]
                if len(field_data) < 1:
                    raise ValueError("Field {} not found in secret {}.".format(search_field, data['overview']['title']))
                return field_data[0]

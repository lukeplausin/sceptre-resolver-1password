from sceptre.resolvers import Resolver
import json
import os
import subprocess


class OnePasswordResolver(Resolver):

    cache = {
        "items": {},
        "documents": {}
    }

    def __init__(self, *args, **kwargs):
        super(OnePasswordResolver, self).__init__(*args, **kwargs)

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

        if "item_list" in self.cache.keys():
            items = self.cache["item_list"]
        else:
            try:
                items = json.loads(subprocess.check_output(['op','list','items']))
            except Exception as e:
                raise RuntimeError(
                    "Error executing the 1password cli: {}".format(e) +
                    "Set up the 1password CLI before using this resolver. " +
                    "https://1password.com/downloads/command-line/"
                )

            self.cache["item_list"] = items
        filtered = [
            item for item in items
            if all(tag in item.get('overview', {}).get('tags', []) for tag in tags)
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
            if uuid in self.cache["items"].keys():
                data = self.cache["items"][uuid]
            else:
                data = json.loads(subprocess.check_output(['op','get','item', uuid]))
                self.cache["items"][uuid] = data
            # need different api calls for doc / vs secret?
            if search_field == 'document':
                if 'documentAttributes' not in data['details'].keys():
                    raise ValueError("Secret {} is not a document.".format(data['overview']['title']))
                else:
                    if data['uuid'] in self.cache["documents"].keys():
                        doc = self.cache["documents"][data['uuid']]
                    else:
                        doc = subprocess.check_output(['op','get','document', data['uuid']]).decode('utf-8')
                        self.cache["documents"][data['uuid']] = data
                    return doc
            else:
                field_data = [
                    field['value'] for field in data['details']['fields']
                    if field['designation'] == search_field
                ]
                if len(field_data) < 1:
                    # Try looking in sections also
                    section_data = [
                        field['v'] 
                            for section in data['details']['sections']
                            for field in section['fields']
                            if field['t'] == search_field
                    ]
                    if len(section_data) < 1:
                        # Try looking in sections also
                        available = ["field: {}".format(field['designation']) for field in data['details']['fields']] + \
                        ["section: {}".format(field['t'])
                            for section in data['details']['sections'] for field in section['fields']]
                        raise ValueError("Field {} not found in secret {}.\nAvailable:\n{}".format(
                            search_field, data['overview']['title'], "\n".join(available)))
                    else:
                        return section_data[0]
                return field_data[0]

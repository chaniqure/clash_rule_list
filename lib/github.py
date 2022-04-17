import json

import requests

from util import logger

log = logger.get_logger('clash')


class GistFile:
    def __init__(self, name, content):
        self.name = name
        self.content = content


class GistCreateRequest:
    def __init__(self, name: str, public: bool, file_list: list[GistFile]):
        self.public = public
        self.description = name
        files = {}
        for file in file_list:
            files[file.name] = {
                'content': file.content
            }
        self.files = files


class Github:

    def __init__(self, token):
        self.__header = {'Authorization': 'token %s' % token}
        self.__param = {'scope': 'gist'}
        self.__api_url = "https://api.github.com/gists"

    def gist_list(self):
        requests.packages.urllib3.disable_warnings()
        return requests.get(self.__api_url, headers=self.__header, params=self.__param, verify=False).text

    def gist_save(self, name, file):
        return self.gist_batch_save(name, [file])

    def gist_batch_save(self, name, files):
        file = self.__get_gist_id(name)
        if file is None:
            return self.__gist_create(name, files)
        return self.__gist_update(name, files)

    def gist_delete(self, name):
        return requests.delete('{}/{}'.format(self.__api_url, self.__get_gist_id(name)), headers=self.__header,
                               params=self.__param, verify=False).ok

    def __gist_create(self, name, files):
        payload = GistCreateRequest(name, False, files)
        data = json.dumps(obj=payload.__dict__, ensure_ascii=False)
        requests.packages.urllib3.disable_warnings()
        return requests.post(self.__api_url,
                             headers=self.__header,
                             params=self.__param,
                             data=data,
                             verify=False).ok

    def __gist_update(self, name, files):
        payload = GistCreateRequest(name, False, files)
        data = json.dumps(obj=payload.__dict__, ensure_ascii=False)
        return requests.patch('{}/{}'.format(self.__api_url, self.__get_gist_id(name)),
                              headers=self.__header,
                              params=self.__param, data=data,
                              verify=False).ok

    def __get_gist_id(self, name):
        requests.packages.urllib3.disable_warnings()
        gists = json.loads(self.gist_list())
        for d in gists:
            if d['description'] == name:
                return d['id']


if __name__ == '__main__':
    a = GistFile('a', 'aaaaaaa1')
    b = GistFile('b', 'bbbbbbb1')
    data = [a, b]
    # req = GistCreateRequest('test', False, data)
    # json_dumps = json.dumps(obj=a.__dict__, ensure_ascii=False)
    # print(type(json.loads(json_dumps)))
    # payload = GistCreateRequest(files, False, description)
    github = Github('')
    # print(github.gist_list())
    # print(github.gist_batch_save('test', data))
    # github.gist_create('test', 'b', 'bbbbbbbb')
    # github.gist_update('test', '111111111111111111')
    print(github.gist_list())

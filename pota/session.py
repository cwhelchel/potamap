class PotaSession():
    '''This functionality doesn't really exist in the POTA API yet.
        But this class will work with it when it does.
    '''

    def __init__(self, app_key: str, api_key: str):
        '''
        app_key = key received from POTA team
        api_key = user specific api key.
        '''
        self.app_key = app_key
        self.api_key = api_key


if __name__ == '__main__':
    # test case
    s = PotaSession("test", "test")

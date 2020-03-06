from types import SimpleNamespace

### Set up coef_info for Coef_Manager

coef_info = SimpleNamespace(USE_AZURE=None, AZURE_CONNECTION_STRING=None, FILE_PATH=None)
# If you do not use Azure, you MUST use a local coefs folder. See oucass.github.io/Profiles/coefs.html for instructions 
coef_info.USE_AZURE="YES"
# If you are using Azure, retrieve the connection strings from your portal. When one key is being regenerated, the other will be used
coef_info.AZURE_CONNECTION_STRING="***REMOVED***"
# If you are NOT using Azure, put the path to the coefs folder here
coef_info.FILE_PATH=""


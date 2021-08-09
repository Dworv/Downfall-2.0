import toml

# Assumes that we have a toml-based config file.
# Each bot is a section in that file.
# e.g.
# [appbot]
#    secret = "mysecretstring" 

#return a string containing the secret for the specified bot
def load_secret(filename, botname):
    parsed_toml = toml.load(filename)
    return (parsed_toml[botname]['secret'])
    
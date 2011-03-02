import os

ftn_config_dir = os.environ.get('FTN_CONFIG_DIR', '/etc/ftn')
ftn_config_file = os.path.join(ftn_config_dir, 'ftn.cfg')
ftn_data_dir = os.environ.get('FTN_DATA_DIR', '/var/lib/ftn')

def show_defaults():
    for varname, varval in globals().items():
        if varname.startswith('ftn_'):
            print varname, '=', varval

if __name__ == '__main__':
    show_defaults()


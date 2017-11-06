# Do you even batch process bro?

This is a batch processing tool to stage multiple OpenShift services. You can also stage a single OpenShift service because why not?

## Prereqs:

- `pip install click`
  - Use a virtualenv cause you'll have global privileges and don't need `sudo` or `--user` to `pip install click`
- Update Lines 49 and 51 in `oc_services.py` for your prod and non_prod cluster (if need be).
- Updaet Line 60 in `oc_services.py` to reflect your Docker registry URL

## How it works:

#### To batch stage services
1. Run `./oc_services.py batch stage_service [text_file] [namespace]`
  - The `text_file` will contain all the images you want to stage
  - The `namespace` is either `prod` or `non_prod`
2. It will go through all the images you listed in the text file and stage them all one by one.

#### To stage a single service:
1. Run `./oc_services.py stage_service [image_name] [namespace]`
  - The `image_name` will contain the service name and version number, ex: `clot-evolve-cart-client:1.0.20`
  - The `namespace` is either `prod` or `non_prod`
2. It will stage the image you put in the command line.

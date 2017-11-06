#!/usr/bin/env python3.6
# vim: sw=2 ts=2

import click
import re
import json
import subprocess
import sys

CTX_SILENT_MODE = 'silent'
CTX_DEBUG_MODE = 'debug'
STAGE_CMD = 'stage_service'
CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())

def is_silent(ctx):
    return ctx.obj[CTX_SILENT_MODE]

def is_debug(ctx):
    return ctx.obj[CTX_DEBUG_MODE]

@click.group()
@click.option('--silent', is_flag=True, default=False, help='Accept all prompts')
@click.option('--debug', is_flag=True, default=False, help='Verbose output')
@click.pass_context
def cli(ctx, silent, debug):
    ctx.obj[CTX_SILENT_MODE] = silent
    ctx.obj[CTX_DEBUG_MODE] = debug
    click.echo('Silent mode is %s' % (is_silent(ctx) and 'on' or 'off'))
    click.echo('Debug mode is %s' % (is_silent(ctx) and 'on' or 'off'))

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('image')
@click.argument('namespace')
def stage_service(ctx, image, namespace):
    """Stage single OpenShift service"""

    silent = is_silent(ctx)

    if silent:
        click.echo('Staging service {0}'.format(image))
    elif not click.confirm('Stage service {0}?'.format(image)):
        sys.exit(1)

    result = subprocess.check_output('oc config view -o json', shell=True)
    parsed = json.loads(result)

    for value in parsed['contexts']:
        if value['context']['cluster'] == "PROD_CLUSTER_NAME_GOES_HERE": #Add your prod cluster name here
            prod_context = value['name']
        elif value['context']['cluster'] == "NON_PROD_CLUSTER_NAME_GOES_HERE": #Add your non_prod cluster name here
            non_prod_context = value['name']

    IMAGE=image
    IMAGE_SPLIT=image.split(":")
    SERVICE=IMAGE_SPLIT[0]
    VERSION=IMAGE_SPLIT[1]
    NAMESPACE=namespace
    ACTIVE_TAG='active'
    REGISTRY='elsols-docker.jfrog.io/eols'
    PROD_CONTEXT=prod_context
    NON_PROD_CONTEXT=non_prod_context

    click.echo('Service name is: {0}'.format(SERVICE))
    click.echo('Version is: {0}'.format(VERSION))
    click.echo('Namespace is: {0}'.format(NAMESPACE))

    if namespace == 'prod':

        click.echo('Context is: {0}'.format(PROD_CONTEXT))

        import_image_prod = subprocess.Popen('oc --context={0} -n {1} import-image {2}:{3} --from="{4}/{2}:{3}"'.format(PROD_CONTEXT, NAMESPACE, SERVICE, VERSION, REGISTRY), shell=True)
        tag_image_prod = subprocess.Popen('oc --context={0} tag {1}/{2}:{3} {1}/{2}:{4}'.format(PROD_CONTEXT, NAMESPACE, SERVICE, VERSION, ACTIVE_TAG), shell=True)
        rollout_image_prod = subprocess.Popen('oc --context={0} -n {1} rollout latest {2}'.format(PROD_CONTEXT, NAMESPACE, SERVICE, VERSION), shell=True)

    elif namespace == 'non_prod':

        click.echo('Context is: {0}'.format(NON_PROD_CONTEXT))

        import_image_non_prod = subprocess.Popen('oc --context={0} -n {1} import-image {2}:{3} --from="{4}/{2}:{3}"'.format(NON_PROD_CONTEXT, NAMESPACE, SERVICE, VERSION, REGISTRY), shell=True)
        tag_image_non_prod = subprocess.Popen('oc --context={0} tag {1}/{2}:{3} {1}/{2}:{4}'.format(NON_PROD_CONTEXT, NAMESPACE, SERVICE, VERSION, ACTIVE_TAG), shell=True)
        rollout_image_non_prod = subprocess.Popen('oc --context={0} -n {1} rollout latest {2}'.format(NON_PROD_CONTEXT, NAMESPACE, SERVICE, VERSION), shell=True)

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('action', type=click.Choice([STAGE_CMD]))
@click.argument('filename', type=click.Path(exists=True))
@click.argument('namespace')
def batch(ctx, action, filename, namespace):
    """Batch stage OpenShift services"""

    silent = is_silent(ctx)
    filename = click.format_filename(filename)

    if silent:
        click.echo('Batch processing {0}'.format(filename))
    elif not click.confirm('Batch process {0}?'.format(filename)):
        sys.exit(1)

    lines = tuple(open(filename, 'r'))
    for line in lines:
        click.echo(line)
        ctx.invoke(stage_service, image=line, namespace=namespace)

if __name__ == '__main__':
    cli(obj={})

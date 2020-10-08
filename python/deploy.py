import argparse
import docker
import json
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser(
        description="Okta integrated FreeRADIUS deployment using Docker.")
    try:
        with open('arguments.json') as arg_file:
            arguments = json.load(arg_file)
        [parser.add_argument(argument, arguments[argument]["arg"], help=arguments[argument]
                             ["help"], action=arguments[argument]["action"]) for argument in arguments]
        return parser.parse_args()
    except:
        print("Can't Find Argument File - Please reference github for Argument File")
        exit()


def get_containers():
    containers_data = {}
    containers_path = Path('../containers')
    container_dirs = [
        path for path in containers_path.iterdir() if path.is_dir()]
    for container in container_dirs:
        container_context = container / 'container'  # Path to Docker Build Files
        deployer_configs = container / 'deployer'  # Path to Python Configs
        build_config = get_configs(deployer_configs / "build_config.json")
        run_config = get_configs(deployer_configs / "run_config.json")
        containers_data[container.name] = {
            'context': container_context, 'build_config': build_config, 'run_config': run_config}
    return containers_data


def get_configs(config_file):
    try:
        with config_file.open() as f:
            config = json.load(f)
        return config
    except:
        print("Config Collection Failed: {}".format(config_file))
        exit()


def get_deployers(args):
    containers = get_containers()
    deployers = []
    for container in containers:
        context = containers[container]['context']
        build_config = containers[container]['build_config']
        run_config = containers[container]['run_config']
        deployer = Deployer(args, container, context, build_config, run_config)
        deployers.append(deployer)
    return deployers


class Deployer():
    def __init__(self, args, container, context, build_config, run_config):
        self.args = args
        self.name = container
        self.path = str(context)
        self.build_config = build_config
        self.run_config = run_config
        self.client = docker.from_env()  # Expand to allow for other hosts

        self.images = self.set_images()
        self.containers = self.set_containers()
        self.run()

    # Main function of this class - Deploys based on args.
    def run(self):
        print("Beginning Deployment")
        if self.args.build:
            self._build(self)
        if self.args.deploy:
            self._deploy(self)
        if self.args.log:
            print("Not yet implemented")
        if self.args.push:
            print("Push Not Yet Available")
        if self.args.test:
            print("Test Bed Not Yet Developed")
        if self.args.update:
            print("Update not yet available")
        print("Deploment Complete")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def __str__(self):
        return str(self.name)

    def set_images(self):
        build_order = self.build_config["build"]
        images = self.build_config["build"]
        return images

    def set_containers(self):
        return [container for container in self.run_config]


    """ Builds containers for deployer.

    Returns: VOID
    """
    @staticmethod
    def _build(self):
        for image in self.images:
            print("Building - {}".format(image))
            try:
                self.client.images.build(path=self.path, dockerfile=image["file"], tag=image["tag"], forcerm=True)
                print("Successful Build - {}".format(image["tag"]))
            except docker.errors.BuildError:
                print("Failed to Build - {}".format(image["tag"]))
                exit()


    """ Deploys containers
    Returns: VOID
    """
    @staticmethod
    def _deploy(self):
        for container in self.containers:
            config = self.run_config[container]
            print("Deploying - {}". format(container))
            if not self._images_available(self):
                print("Can not deploy Container")
            elif not config["enabled"]:
                print("Container Disabled")
            else:
                image = config["image"]
                ports = config["ports"]
                environment = config["environment"]
                self.client.containers.run(image, name=container, detach=config["detach"], privileged=config["privileged"], ports=ports, environment=environment)



    """ Checks if docker host has images available for deployment.
        Intended to fail deploy if not all images are present.

    Returns:
        [bool] -- True if all images present | False if missing any.
    """
    @staticmethod
    def _images_available(self):
        try:
            [self.client.images.get(image["tag"]) for image in self.images]
            return True
        except docker.errors.ImageNotFound:
            return False

    @staticmethod
    def _containers_status(self):
        status = []
        for container in self.containers:
            try:
                status.append(self.client.containers.get(container).status)
            except docker.errors.NotFound:
                status.append("none")
        return status


if __name__ == "__main__":
    print("Deployer Base Class Testing")
    args = get_args()
    deployers = get_deployers(args)
    [print(deployer) for deployer in deployers]
    print("We made it all the way")

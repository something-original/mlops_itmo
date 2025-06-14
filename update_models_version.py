import yaml
import subprocess


def update_models_version():
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    current_version = config['models']['version']
    version_num = int(current_version.replace('v', ''))
    next_version = version_num + 1
    next_tag = f'v{next_version}'

    subprocess.run(['dvc', 'add', 'models/master.pt'], check=True)
    subprocess.run(['dvc', 'add', 'models/parseq.pt'], check=True)
    subprocess.run(['dvc', 'add', 'models/scores.json'], check=True)
    subprocess.run(['git', 'tag', next_tag], check=True)
    subprocess.run(['dvc', 'commit'], check=True)
    subprocess.run(['dvc', 'push'], check=True)

    config['models']['version'] = next_tag
    with open('app/config.yaml', 'w') as f:
        yaml.dump(config, f)

    open('models_pushed.flag', 'a').close()


if __name__ == '__main__':
    update_models_version()
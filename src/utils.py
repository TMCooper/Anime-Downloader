import json, os, platform, subprocess
from InquirerPy import inquirer
from InquirerPy.base import Choice

class Utils:
    global PATH_LANGUAGE
    global PATH

    PATH = os.getcwd()
    PATH_LANGUAGE_FOLDER = os.path.join(PATH, "ressources", "languages")
    PATH_LANGUAGE = os.path.join(PATH_LANGUAGE_FOLDER, "languages.json")

    API_TO_LAUNCH = {
        "fr": [
            Choice(name="AnimeSama", value="animeSama"),
            Choice(name="Voiranime", value="voiranime"),
            Choice(name="Toute", value="all")
        ],
        "eng": [
            Choice(name="AnimeSama", value="animeSama"),
            Choice(name="Voiranime", value="voiranime"),
            Choice(name="All", value="all")
        ],
    }

    @staticmethod
    def ask(question, options):
        choix = inquirer.select(
            message=question,
            choices=options
            ).execute()
        return choix

    @staticmethod
    def getLanguages():
        with open(PATH_LANGUAGE, "r", encoding='utf-8') as data:
            languages = json.load(data)

        return languages
    
    @staticmethod
    def clearScreen():
        if platform.system() == "Windows":
            os.system("cls")
        elif platform.system() in ["Linux", "Darwin"]:
            os.system("clear")

    @staticmethod
    def _api_env(api_path):
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = os.path.join(api_path, ".venv")
        return env

    @staticmethod
    def _setup_api_venv(api_path):
        env = Utils._api_env(api_path)
        venv_path = os.path.join(api_path, ".venv")
        if not os.path.exists(venv_path):
            subprocess.run(['uv', 'venv'], cwd=api_path, env=env, check=True)
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'], cwd=api_path, env=env, check=True)

    @staticmethod
    def animesama_api():
        api_dir = os.path.join(PATH, "API")
        anime_sama_path = os.path.join(api_dir, "AnimeSamaApi")
        if not os.path.exists(anime_sama_path):
            os.makedirs(api_dir, exist_ok=True)
            subprocess.run(['git', 'clone', 'https://github.com/TMCooper/AnimeSamaApi.git'], cwd=api_dir, check=True)
        else:
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=anime_sama_path, check=True)

    @staticmethod
    def voiranime_api():
        api_dir = os.path.join(PATH, "API")
        voiranime_path = os.path.join(api_dir, "voiranime_API")
        if not os.path.exists(voiranime_path):
            os.makedirs(api_dir, exist_ok=True)
            subprocess.run(['git', 'clone', 'https://github.com/TMCooper/voiranime_API.git'], cwd=api_dir, check=True)
        else:
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=voiranime_path, check=True)

    @staticmethod
    def prepare_anime_sama():
        Utils.animesama_api()
        anime_sama_path = os.path.join(PATH, "API", "AnimeSamaApi")
        Utils._setup_api_venv(anime_sama_path)
        return anime_sama_path

    @staticmethod
    def prepare_voiranime():
        Utils.voiranime_api()
        voiranime_path = os.path.join(PATH, "API", "voiranime_API")
        Utils._setup_api_venv(voiranime_path)
        return voiranime_path

    @staticmethod
    def launchApis(api_choices):
        if api_choices == "animesama":
            # Recupère le repo de l'api animesama
            anime_sama_path = Utils.prepare_anime_sama()
            subprocess.run(
                ['uv', 'run', '--no-project', '--active', 'main.py'],
                cwd=anime_sama_path,
                env=Utils._api_env(anime_sama_path)
            )

        elif api_choices == "voiranime":
            # Recupère le repo de l'api voiranime
            voiranime_path = Utils.prepare_voiranime()
            subprocess.run(
                ['uv', 'run', '--no-project', '--active', 'main.py'],
                cwd=voiranime_path,
                env=Utils._api_env(voiranime_path)
            )

        else:
            # Recupère les deux apis
            anime_sama_path = Utils.prepare_anime_sama()
            voiranime_path = Utils.prepare_voiranime()

            p_animesama = subprocess.Popen(
                ['uv', 'run', '--no-project', '--active', 'main.py'],
                cwd=anime_sama_path,
                env=Utils._api_env(anime_sama_path)
            )
            p_voiranime = subprocess.Popen(
                ['uv', 'run', '--no-project', '--active', 'main.py'],
                cwd=voiranime_path,
                env=Utils._api_env(voiranime_path)
            )
            try:
                p_animesama.wait()
                p_voiranime.wait()
            except KeyboardInterrupt:
                p_animesama.terminate()
                p_voiranime.terminate()
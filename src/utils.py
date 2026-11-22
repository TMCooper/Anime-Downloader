import json, os, platform, subprocess, threading, atexit, time, socket
from InquirerPy import inquirer
from InquirerPy.base import Choice

class Utils:
    _api_processes = []

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
    def _wait_for_port(process, port, host="127.0.0.1", timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                print(f"[ERREUR] L'API sur le port {port} s'est arrêtée toute seule.")
                return False
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return True
            except OSError:
                time.sleep(0.2)
        print(f"[ERREUR] Timeout : l'API sur le port {port} n'a pas démarré.")
        return False

    @staticmethod
    def _run_single_api(prepare_func, port):
        api_path = prepare_func()
        
        p = subprocess.Popen(
            ['uv', 'run', '--no-project', '--active', 'main.py'],
            cwd=api_path,
            env=Utils._api_env(api_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        Utils._api_processes.append(p)

        # Attend que le serveur réponde avant de lacher le thread
        Utils._wait_for_port(p, port)

    @staticmethod
    def _setup_api_venv(api_path):
        env = Utils._api_env(api_path)
        venv_path = os.path.join(api_path, ".venv")
        if not os.path.exists(venv_path):
            subprocess.run(['uv', 'venv'], cwd=api_path, env=env, check=True)
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'], cwd=api_path, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def animesama_api():
        api_dir = os.path.join(PATH, "API")
        anime_sama_path = os.path.join(api_dir, "AnimeSamaApi")
        if not os.path.exists(anime_sama_path):
            os.makedirs(api_dir, exist_ok=True)
            subprocess.run(['git', 'clone', 'https://github.com/TMCooper/AnimeSamaApi.git'], cwd=api_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=anime_sama_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def voiranime_api():
        api_dir = os.path.join(PATH, "API")
        voiranime_path = os.path.join(api_dir, "voiranime_API")
        if not os.path.exists(voiranime_path):
            os.makedirs(api_dir, exist_ok=True)
            subprocess.run(['git', 'clone', 'https://github.com/TMCooper/voiranime_API.git'], cwd=api_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=voiranime_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

    def launchApis(api_choices):
        atexit.register(Utils.stopApis)

        tasks = []
        if api_choices == "animesama":
            tasks.append((Utils.prepare_anime_sama, 5000))
        elif api_choices == "voiranime":
            tasks.append((Utils.prepare_voiranime, 8000))
        else:
            tasks.extend([
                (Utils.prepare_anime_sama, 5000),
                (Utils.prepare_voiranime, 8000)
            ])

        threads = []
        for prepare_func, port in tasks:
            t = threading.Thread(
                target=Utils._run_single_api,
                args=(prepare_func, port),
                daemon=True
            )
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        

    @staticmethod
    def stopApis():
        for p in Utils._api_processes:
            if p.poll() is None:
                p.terminate()
import os
from src.utils import Utils
from YoitsuWrap.Config import Config
from YoitsuWrap.Anime import Anime

PATH = os.getcwd()
DOWNLOAD_PATH = os.path.join(PATH, "Anime")

def main():
    try :
        Utils.clearScreen()
        languages = Utils.getLanguages()
        language = "defaults"

        language = Utils.ask(languages[language]["askLangues"], languages[language]["languagesOptions"]).lower()
        Utils.clearScreen()

        api_choices = Utils.ask(languages[language]["apiChoices"], Utils.API_TO_LAUNCH.get(language)).lower()
        Utils.launchApis(api_choices)

        if api_choices == "animesama":
            config = Config.create_config(urls=["http://127.0.0.1"], ports=[5000], path=DOWNLOAD_PATH, sources=["ANIMESAMA"])
        elif api_choices == "voiranime":
            config = Config.create_config(urls=["http://127.0.0.1"], ports=[8000], path=DOWNLOAD_PATH, sources=["VOIRANIME"])
        else:
            config = Config.create_config(urls=["http://127.0.0.1"], ports=[5000, 8000], path=DOWNLOAD_PATH, sources=["ANIMESAMA", "VOIRANIME"])

        Utils.clearScreen()

        title = input(languages[language]["animeTitleChoice"])
        version = Utils.ask(languages[language]["animeVersion"], ["vostfr", "vf"])
        Utils.clearScreen()

        anime = Anime.search_by_name(title=title, version=version, config=config)
        # Faire en sorte de regarder le nombre de saison disponible et voir pour donner la possibilité a l'utilisateur d'en choisir une ou plusieur / toute
        anime.download_all() # Temporaire mais fonctionnelle télécharge tous se qui est disponibles sur l'anime et reuni grace au wrapper

    except KeyboardInterrupt:
        Utils.stopApis()
        print("\nStop...")

if __name__ == "__main__":
    main()
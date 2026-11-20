from src.utils import Utils
import YoitsuWrap

def main():
    Utils.clearScreen()
    languages = Utils.getLanguages()
    language = "defaults"

    language = Utils.ask(languages[language]["askLangues"], languages[language]["languagesOptions"]).lower()
    Utils.clearScreen()

    api_choices = Utils.ask(languages[language]["apiChoices"], Utils.API_TO_LAUNCH.get(language)).lower()
    print(Utils.launchApis(api_choices))
    # Utils.clearScreen()

if __name__ == "__main__":
    main()
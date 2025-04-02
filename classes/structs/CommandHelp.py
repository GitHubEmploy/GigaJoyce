from typing import Optional, Callable, Dict

class CommandHelp:
    """
    Classe para definir ajuda detalhada de comandos com suporte a múltiplos idiomas.
    """

    def __init__(
        self, 
        name: str, 
        translations: Dict[str, Dict[str, Optional[str]]]
    ):
        """
        Inicializa o CommandHelp com traduções.

        Args:
            name (str): Nome do comando.
            translations (Dict[str, Dict[str, Optional[str]]]): 
                Dicionário onde a chave é o código do idioma e o valor é outro dicionário contendo 'description', 'usage', e 'examples'.
                Exemplo:
                {
                    "en": {
                        "description": "Shows the current XP and level of a user.",
                        "usage": "/xp [user]",
                        "examples": ["/xp", "/xp @User123"]
                    },
                    "pt": {
                        "description": "Mostra o XP atual e o nível de um usuário.",
                        "usage": "/xp [usuário]",
                        "examples": ["/xp", "/xp @Usuario123"]
                    }
                }
        """
        self.name = name  
        self.translations = translations 

    def get_translation(self, language: str) -> Dict[str, Optional[str]]:
        """
        Retorna as traduções para o idioma especificado. Se não existir, retorna inglês como padrão.

        Args:
            language (str): Código do idioma.

        Returns:
            Dict[str, Optional[str]]: Dicionário com 'description', 'usage', e 'examples'.
        """
        return self.translations.get(language, self.translations.get("en", {}))

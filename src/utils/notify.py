import requests


class Notify:
    def __init__(self, api_url):
        """
        Inicializa la clase Notify con la URL del endpoint.

        :param api_url: URL del endpoint al que se enviarán las notificaciones.
        """
        self.api_url = api_url

    def send(self, data):
        """
        Envía una notificación con el objeto JSON al endpoint.

        :param data: Diccionario con los datos a enviar.
        :return: Respuesta del servidor o mensaje de error.
        """
        try:
         
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            return (
                response.json()
            )  # Retorna la respuesta del servidor como un objeto JSON
        except requests.exceptions.RequestException as e:
            if e.response:
                try:
                    error_response = e.response.json()  # Intentamos obtener el contenido JSON de la respuesta
                    print(f"Error message: {error_response.get('message')}")
                    print(f"Error details: {error_response.get('details')}")
                except ValueError:
                    # Si no se puede decodificar JSON, imprimimos el contenido de la respuesta
                    print(f"Response content: {e.response.text}")
            else:
                print(f"Error: {e}")


# Ejemplo de uso
# if __name__ == "__main__":
#     # Inicializa la clase Notify con la URL del endpoint
#     api_url = "https://ms-gateway.quartup.app/api/helpdesk/ticket/store-from-sv2"
#     notifier = Notify(api_url)

#     # Crea el objeto JSON para enviar
#     notification_data = {
#         "attachments": None,
#         "description": "test",
#         "email": "mg.jmanuel@gmail.com",
#         "name": "Jose Manuel (Tempo Logistics Smart S.L.)",
#         "recipient": "soporte@quartup.helpdeskq.app",
#         "subdomain": "quartup",
#         "subject": "test",
#         "tenant_id": "6269744aa9da50110432ceb7"
#     }

#     # Envía la notificación
#     response = notifier.send(notification_data)
#     if response:
#         print("Notificación enviada correctamente:", response)
#     else:
#         print("Error al enviar la notificación.")

from service.imagepullsecret_service import ImagepullsecretService


def main():
    svc = ImagepullsecretService()

    svc.scan()
    svc.clean_up()


if __name__ == '__main__':
    main()

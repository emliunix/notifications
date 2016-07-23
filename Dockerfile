FROM debian

MAINTAINER 刘宇辉 <emliunix@clojurians.org>

RUN apt-get -y update \
    && apt-get -y install python-twisted python-lxml python-cssselect \
    && apt-get -y clean
ADD . /app
WORKDIR /app
CMD python main.py --url $HOOK_URL --token $HOOK_TOKEN
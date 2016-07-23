# -*- coding: utf-8 -*-

from notifications import settings
from twisted.web import client
from twisted.internet import task, reactor, defer, endpoints
from lxml import html, cssselect
from argparse import ArgumentParser
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("notifications")

sel_base = cssselect.CSSSelector(settings.selector)
sel_chapter_name = cssselect.CSSSelector(settings.selector_chapter_name)
sel_update_date = cssselect.CSSSelector(settings.selector_update_date)

@defer.inlineCallbacks
def job():
    logger.info("Getting page")
    txt = yield client.getPage(settings.url)
    parsed_txt = html.fromstring(txt)
    # pylint:disable=E1102
    el = sel_base(parsed_txt)
    # if element does not exist
    if not len(el):
        return
    chapter_name = sel_chapter_name(el[0])[0].text.strip()
    update_date = sel_update_date(el[0])[0].text.strip()

    # do nothing if no new chapter avaliable
    if settings.current_chapter == chapter_name:
        logger.info("Current chapter is %s, not a new chapter, do nothing.", chapter_name)
        return
    else:
        # saves the new chapter name to settings
        settings.current_chapter = chapter_name

    data = {
        "chapter_name": chapter_name,
        "update_date": update_date
    }
    logger.info("{\n\tchapter_name: %s,\n\tupdate_date: %s\n}", chapter_name, update_date)

    logger.info("Sending data to webhook: %s", settings.webhook_url)
    try:
        yield client.getPage(settings.webhook_url,
                            method="POST", postdata=json.dumps(data),
                            headers={"Content-Type": "application/json; chatset=utf-8"})
    except Exception as exc:
        logger.error("Error occured while sending data.\n%s", str(exc))
    else:
        logger.info("Data sent")

def done(r):
    logger.info("Loop finished")

def failed(err):
    logger.error("An error occured while looping.\n%s", str(err))

def work():
    # run the job in reactor
    # pylint:disable=E1121
    logger.info("Running job...")
    job()

# pylint:disable=E1101
def run():

    parser = ArgumentParser()
    parser.add_argument("--token", type=str, help="Webhook token")
    parser.add_argument("--url", type=str, help="Site url")
    args = parser.parse_args(sys.argv[1:])
    settings.hook_site_url = args.url
    settings.hook_token = args.token
    settings.webhook_url = "%s/hooks/%s" % (settings.hook_site_url, settings.hook_token)

    logger.info("Start looping")
    d = task.LoopingCall(work).start(settings.delay, True)
    d.addCallback(done)
    d.addErrback(failed)

    reactor.run()

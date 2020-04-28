#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up what I got from Case
"""

from airtight.cli import configure_commandline
from bs4 import BeautifulSoup, NavigableString, Comment
from difflib import SequenceMatcher
import logging
from os import walk
from pathlib import Path
from shutil import copyfile
import re
import sys

dryrun = False
logger = logging.getLogger(__name__)
rx = re.compile(r'\s+')

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR',
        False],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)',
        False],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)', False],
    ['-d', '--dryrun', False, 'do not change anything', False]
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ['where', str, 'top-level directory']
]


def notifier(context_str, logger):
    global rx

    maxlen = 130
    notice = rx.sub(' ', context_str.replace('\n', ' ')).strip().split()
    for i in range(0, len(notice)):
        if len(' '.join(notice[0:i])) >= maxlen:
            break
    while len(' '.join(notice[0:i])) > maxlen:
        i = i - 1
    suffix = ''
    if i < len(notice):
        suffix = ' ... '
    notice = ' '.join(notice[0:i]) + suffix
    logger.debug(
        ' REMOVING: {}'.format(notice))


def clean_links(soup):
    for ele in soup.select('a'):
        if ele['href'] == '../index.html':
            pass
        elif ele['href'] == 'http://www.rz.uni-frankfurt.de/~clauss/':
            pass
        elif ele['href'] == 'index.html#methods':
            pass
        elif ele['href'] == 'http://classics.case.edu/asgle/abbrev/latin/#limitations':
            ele['href'] = '#limitations'
        elif 'mailto:tom_elliott@unc.edu' in ele['href']:
            ele['href'] = 'mailto:ipse@paregorios.org?subject=Abbreviations in Latin Inscriptions'
            ele.string.replace_with('ipse@paregorios.org')
        elif not ele['href'].startswith('pop'):
            if not ele['href'].startswith('noref'):
                if ele['href'].startswith('http://classicsstaging.case.edu/noref'):
                    ele['href'] = ele['href'].replace('http://classicsstaging.case.edu/', '')
                else:
                    raise ValueError(str(ele))
    return soup


def out_vile_jelly(ele):
    notifier(str(ele), logger)
    ele.decompose()


def clean(filepath: Path):
    global dryrun

    logger = logging.getLogger(sys._getframe().f_code.co_name)
    logger.info(' FILE TO CLEAN: {}'.format(filepath))
    backpath = filepath.parent / (filepath.name + '.bak')
    logger.debug(' BACKUP FILE: {}'.format(backpath))
    if not dryrun:
        copyfile(filepath, backpath)
    with open(filepath, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'lxml')
    del fp
    orig_html = str(soup)

    # get rid of comments
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # strip out all tags that we don't need at all
    bad_tags = [
        'script', 'style'
    ]
    for tag in bad_tags:
        for ele in soup.select(tag):
            out_vile_jelly(ele)

    # strip out tag + attribute combinations that we don't want
    bad_tags_attrs = {
        'meta': {
            'http-equiv': ['X-UA-Compatible'],
            'name': ['viewport', 'generator']
        },
        'div': {
            'id': [
                'cas-top-slider-panel', 'cas-top-bar', 'cas-department-menu',
                'cas-mobile-top-bar', 'cas-mobile-menu-slider-toggle',
                'cas-mobile-department-menu', 'cas-footer'
            ],
            'class': ['navigation']
        }
    }
    for bad_tag, bad_attrs in bad_tags_attrs.items():
        for attr, attr_vals in bad_attrs.items():
            for attr_val in attr_vals:
                junk = soup.find_all(bad_tag, {attr: attr_val})
                for ele in junk:
                    out_vile_jelly(ele)

    # strip out complicated structure that we don't want
    ele = soup.find('div', {'id': 'cas-breadcrumbs'})
    if ele is None:
        raise RuntimeError('foo')
    ele = ele.find_parent('div', {'class': 'container'})
    if ele is None:
        raise RuntimeError('bar')
    out_vile_jelly(ele)
    ele = soup.find('ul', {'id': 'cas-left-navigation'})
    if ele is None:
        logger.warning('Did not find "cas-left-navigation"')
    else:
        out_vile_jelly(ele.parent)

    elements = soup.find_all('a')
    jellies = []
    for ele in elements:
        try:
            ele['href']
        except TypeError:
            raise RuntimeError(ele)
        if 'asgle-logo.gif' in ele['href']:
            if ele.parent.name == 'p':
                jellies.append(ele.parent)
            else:
                raise RuntimeError('vorpal rabbit')
    for jelly in jellies:
        out_vile_jelly(jelly)

    # fix or strip out undesireable links that didn't get removed in previous code
    soup = clean_links(soup)

    # remove Case postfix from page title
    ele = soup.find('title')
    title = str(ele.string)
    if '| Department of Classics' in title:
        title = title.replace('| Department of Classics', '').strip()
        logger.debug('replacing title string "{}" with "{}"'.format(
            ele.string, title
        ))
        new_tag = soup.new_tag('title')
        ele.replace_with(new_tag)
        new_tag.string = title

    # unwrap container/formatting divs
    layers = ['div', 'div.row', 'div.container']
    for i, tag_class in enumerate(layers):
        selector = 'body'
        for j in range(len(layers), i, -1):
            selector += ' > {}'.format(layers[j-1])
        elements = soup.select(selector)
        for ele in elements:
            ele.unwrap()

    # save result to file
    soup.smooth()
    new_html = str(soup)
    s = SequenceMatcher(a=orig_html, b=new_html)
    r = s.real_quick_ratio()
    logger.info(
        'delta {}: {}%'.format(
            filepath.name,
            round(100.0 * (1.0 - r))))
    if not dryrun:
        with open(filepath, 'w', encoding='utf-8') as fp:
            fp.write(new_html)
        del fp


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    global dryrun
    dryrun = kwargs['dryrun']
    if dryrun:
        logger.info(' DRY RUN: no files will be changed.')
    where = Path(kwargs['where']).resolve()
    logger.info(' WHERE: {}'.format(where))
    for root, dirs, files in walk(where):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        try:
            dirs.remove('scripts')
        except ValueError:
            pass
        for fn in files:
            if fn.endswith('.html'):
                clean(Path(root) / fn)


if __name__ == "__main__":
    main(**configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL))

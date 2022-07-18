import logging
from typing import List, Generator, Tuple

import bioc
import nltk
from bioc import BioCPassage, BioCDocument


def split_newline(text: str, sep='\n') -> Generator[Tuple[str, int], None, None]:
    """
    Split the text based on sep (default: \n).
    """
    lines = text.split(sep)
    offset = 0
    for line in lines:
        offset = text.index(line, offset)
        yield line, offset
        offset += len(line)


def no_split_newline(text):
    yield text, 0


def split(text: str, newline: bool = False) -> Generator[Tuple[str, int], None, None]:
    """
    Split the text using nltk sent_tokenize.

    Yields:
         (sentence, offset)
    """
    if len(text) == 0:
        return

    if newline:
        line_splitter = split_newline
    else:
        line_splitter = no_split_newline

    for line, line_offset in line_splitter(text):
        sent_list = nltk.sent_tokenize(line)  # type: List[str]
        offset = 0
        for sent in sent_list:
            offset = line.find(sent, offset)
            if offset == -1:
                raise IndexError('Cannot find %s in %s' % (sent, text))
            yield sent, offset + line_offset
            offset += len(sent)


class NegBioSSplitter:
    """NLTK sentence splitter"""

    def __init__(self, newline: bool = False):
        """
        Args:
            newline: split the newline.
        """
        super(NegBioSSplitter, self).__init__()
        self.newline = newline
        self.logger = logging.getLogger(__name__)

    def process_passage(self, passage: BioCPassage) -> BioCPassage:
        """
        Split text into sentences with offsets.
        """
        try:
            sentences = list(split(passage.text, self.newline))
        except IndexError as e:
            self.logger.error('%s:%s: %s', passage.infons['docid'], passage.offset, str(e))
            return passage

        del passage.sentences[:]
        for text, offset in sentences:
            sentence = bioc.BioCSentence()
            sentence.infons['docid'] = passage.infons['docid']
            sentence.offset = offset + passage.offset
            sentence.text = text
            passage.add_sentence(sentence)
        return passage

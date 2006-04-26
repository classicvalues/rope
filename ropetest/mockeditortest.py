import unittest

from ropetest.mockeditor import *
from rope.editor import *

class EditorFactory(object):
    def create(self):
        pass

class GraphicalEditorFactory(EditorFactory):
    _frame = None
    def create(self):
        if not GraphicalEditorFactory._frame:
            GraphicalEditorFactory._frame = Frame()
        return GraphicalEditor(GraphicalEditorFactory._frame)

class MockEditorFactory(EditorFactory):
    def create(self):
        return MockEditor()

class TextEditorTest(unittest.TestCase):

    _editorFactory = GraphicalEditorFactory()
    def __init__(self, *args, **kws):
        self.__factory = self.__class__._editorFactory
        unittest.TestCase.__init__(self, *args, **kws)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.editor = self.__factory.create()
        self.editor.set_text('sample text')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSetGetText(self):
        self.assertEquals('sample text', self.editor.get_text())
        self.editor.set_text('')
        self.assertEquals('', self.editor.get_text())

    def testTextIndices(self):
        self.assertTrue(self.editor.get_start() < self.editor.get_end())
        self.editor.set_text('')
        self.assertEquals(self.editor.get_start(), self.editor.get_insert())
        self.assertEquals(self.editor.get_insert(), self.editor.get_end())

    def testTextIndicesMoving(self):
        index = self.editor.get_insert()
        newIndex = self.editor.get_relative(index, 2)
        self.assertTrue(index < newIndex)
        self.assertEquals(index, self.editor.get_relative(newIndex, -2))

    def testTextIndicesMovingOutOfBounds(self):
        index = self.editor.get_start()
        self.assertEquals(self.editor.get_relative(index, 100), self.editor.get_end())
        self.assertEquals(self.editor.get_relative(index, -100), self.editor.get_start())

    def testAbsoluteTextIndicesMovingOutOfBounds(self):
        index = self.editor.get_start()
        self.assertEquals(self.editor.get_index(100), self.editor.get_end())
        self.assertEquals(self.editor.get_index(-100), self.editor.get_start())

    def testMovingInsertIndex(self):
        self.assertEquals(self.editor.get_start(), self.editor.get_insert())
        self.editor.set_insert(self.editor.get_index(3))
        self.assertEquals(self.editor.get_index(3), self.editor.get_insert())

    def testReading(self):
        self.assertEquals('s', self.editor.get())
        
    def testReadingAnyIndex(self):
        self.assertEquals('a', self.editor.get(self.editor.get_index(1)))

    def testReadingRanges(self):
        self.assertEquals('sample', self.editor.get(self.editor.get_start(),
                                                    self.editor.get_index(6)))

    def testInsertingText(self):
        self.editor.insert(self.editor.get_index(6), ' tricky')
        self.assertEquals('sample tricky text', self.editor.get_text())

    def testInsertingTextAtTheEnd(self):
        self.editor.insert(self.editor.get_end(), ' note')
        self.assertEquals('sample text note', self.editor.get_text())

    def testInsertingTextAtTheBeginning(self):
        self.editor.insert(self.editor.get_start(), 'new ')
        self.assertEquals('new sample text', self.editor.get_text())

    def testReadingAtTheEnd(self):
        self.assertEquals('', self.editor.get(self.editor.get_end()))

    def testMultiLineContent(self):
        self.editor.insert(self.editor.get_end(), '\nanother piece of text')
        self.assertEquals('sample text\nanother piece of text', self.editor.get_text())
        self.assertEquals('text',
                          self.editor.get(self.editor.get_relative(self.editor.get_end(), -4), 
                                          self.editor.get_end()))
        self.assertEquals('a', self.editor.get(self.editor.get_index(12)))

    def testDeleting(self):
        self.editor.delete()
        self.assertEquals('ample text', self.editor.get_text())
        self.editor.set_insert(self.editor.get_index(3))
        self.editor.delete()
        self.editor.delete()
        self.assertEquals('amp text', self.editor.get_text())
    
    def testDeletingFromTheMiddle(self):
        self.editor.delete(self.editor.get_index(1), 
                                self.editor.get_index(7))
        self.assertEquals('stext', self.editor.get_text())
        self.editor.delete(self.editor.get_index(2), 
                                self.editor.get_end())
        self.assertEquals('st', self.editor.get_text())

    def testDeletingFromTheEnd(self):
        self.editor.delete(self.editor.get_end())
        self.assertEquals('sample text', self.editor.get_text())

    def testMultiLineDeleting(self):
        self.editor.insert(self.editor.get_end(), '\nanother piece of text')
        self.editor.delete(self.editor.get_index(11))
        self.assertEquals('sample textanother piece of text', self.editor.get_text())

    def testMoveNextWord(self):
        self.editor.nextWord()
        self.assertEquals(' ', self.editor.get(), 'Expected <%c> but was <%c>' % (' ', self.editor.get()))

    def testMoveNextWordOnSpaces(self):
        self.editor.nextWord()
        self.editor.insert(self.editor.get_end(), ' and\n')
        self.editor.nextWord()
        self.assertEquals(' ', self.editor.get())
        self.editor.nextWord()
        self.assertEquals('\n', self.editor.get())

    def testNextWordOnEnd(self):
        self.editor.set_insert(self.editor.get_end())
        self.editor.nextWord()
        self.assertEquals(self.editor.get_end(), self.editor.get_insert())

    def testNextWordOnNewLine(self):
        self.editor.set_insert(self.editor.get_relative(self.editor.get_end(), -1))
        self.editor.insert(self.editor.get_end(), '\non a new line')
        self.editor.nextWord()
        self.assertEquals('\n', self.editor.get())

    def testNextWordOnNewLine(self):
        self.editor.set_text('hello \n world\n')
        self.editor.nextWord()
        self.editor.nextWord()
        self.assertEquals('\n', self.editor.get(), self.editor.get())

    def testNextOneCharacterWord(self):
        self.editor.set_text('1 2\n')
        self.editor.nextWord()
        self.assertEquals(' ', self.editor.get())
        self.editor.nextWord()
        self.assertEquals('\n', self.editor.get())

    def testPrevWordOnTheBegining(self):
        self.editor.prevWord()
        self.assertEquals('s', self.editor.get())

    def testPrevWord(self):
        self.editor.set_insert(self.editor.get_end())
        self.editor.prevWord()
        self.assertEquals('t', self.editor.get())
        self.editor.prevWord()
        self.assertEquals('s', self.editor.get())

    def testPrevWordOnTheMiddleOfAWord(self):
        self.editor.set_insert(self.editor.get_relative(self.editor.get_end(), -2))
        self.editor.prevWord()
        self.assertEquals('t', self.editor.get())

    def testPrevOneCharacterWord(self):
        self.editor.set_text('1 2 3')
        self.editor.set_insert(self.editor.get_end())
        self.editor.prevWord()
        self.assertEquals('3', self.editor.get())
        self.editor.prevWord()
        self.assertEquals('2', self.editor.get())
        self.editor.prevWord()
        self.assertEquals('1', self.editor.get())

    def testDeletingNextWord(self):
        self.editor.deleteNextWord()
        self.assertEquals(' text', self.editor.get_text())

    def testDeletingNextWordInTheMiddle(self):
        self.editor.set_insert(self.editor.get_index(2))
        self.editor.deleteNextWord()
        self.assertEquals('sa text', self.editor.get_text())

    def testDeletingPrevWord(self):
        self.editor.set_insert(self.editor.get_end())
        self.editor.deletePrevWord()
        self.assertEquals('sample ', self.editor.get_text(), self.editor.get_text())

    def testDeletingPrevWordInTheMiddle(self):
        self.editor.set_insert(self.editor.get_relative(self.editor.get_end(), -2))
        self.editor.deletePrevWord()
        self.assertEquals('sample xt', self.editor.get_text(), self.editor.get_text())

    def testDeletingPrevWordAtTheBeginning(self):
        self.editor.set_insert(self.editor.get_index(3))
        self.editor.deletePrevWord()
        self.assertEquals('ple text', self.editor.get_text(), self.editor.get_text())

    def testGoingToTheStart(self):
        self.editor.set_insert(self.editor.get_index(3))
        self.editor.goToTheStart()
        self.assertEquals(self.editor.get_start(), self.editor.get_insert())

    def testGoingToTheStart(self):
        self.editor.set_insert(self.editor.get_index(3))
        self.editor.goToTheEnd()
        self.assertEquals(self.editor.get_end(), self.editor.get_insert())

    def test_searching(self):
        found = self.editor.search('s', self.editor.get_insert())
        self.assertEquals(self.editor.get_start(), found)

    def test_searching_not_found(self):
        found = self.editor.search('aa', self.editor.get_insert())
        self.assertTrue(found is None)

    def test_reverse_searching(self):
        self.editor.set_insert(self.editor.get_index(len('sample text') - 1))
        found = self.editor.search('te', self.editor.get_insert(), forwards=False)
        self.assertEquals(self.editor.get_index(7), found)

    def test_case_sensetivity(self):
        self.editor.set_text('aAb')
        self.assertTrue(self.editor.search('aB', self.editor.get_insert()) is None)
        self.assertTrue(self.editor.search('aB', self.editor.get_insert(), case = False) is not None)


def suite():
    result = unittest.TestSuite()
    TextEditorTest._editorFactory = GraphicalEditorFactory()
    result.addTests(unittest.makeSuite(TextEditorTest))
    TextEditorTest._editorFactory = MockEditorFactory()
    result.addTests(unittest.makeSuite(TextEditorTest))
    return result


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
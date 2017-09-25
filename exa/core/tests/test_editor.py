# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.editor`
#############################################
Test the text manipulation engine.
"""
import os
import bz2
import gzip
import shutil
from uuid import uuid4
from io import StringIO
from unittest import TestCase
from tempfile import mkdtemp
from exa.core.editor import Match, Matches, Found, Editor
# Python 2 compatibility
if not hasattr(bz2, "open"):
    bz2.open = bz2.BZ2File


class TestAuxiliary(TestCase):
    """
    Tests for :class:`~exa.core.editor.Match`, :class:`~exa.core.editor.Matches`,
    and :class:`~exa.core.editor.Found`.
    """
    def setUp(self):
        self.matches = [Match(i, "text") for i in range(3)]
        self.patterns = [Matches("text", *self.matches), Matches("stuff")]

    def test_match(self):
        self.assertEqual(self.matches[0].num, 0)
        self.assertEqual(self.matches[0].text, "text")

    def test_pattern(self):
        self.assertEqual(self.patterns[1]._pattern, "stuff")
        self.assertEqual(len(self.patterns[0]), 3)
        self.patterns[0].add(Match(4, "stuff"))
        self.assertEqual(len(self.patterns[0]), 4)

    def test_found(self):
        found = Found(*self.patterns)
        self.assertEqual(len(found), 2)


class TestEditor(TestCase):
    """Test the methods of the editor class."""
    def setUp(self):
        """
        Since the editor support file I/O, generate some test files on which
        to test the various reading functions.
        """
        self.text = u"""Example text, {tmp},
                    used to test the editor."""
        self.dirpath = mkdtemp()
        self.path = os.path.join(self.dirpath, uuid4().hex)
        with open(self.path, 'wb') as f:
            f.write(self.text.encode())
        with open(self.path, "rb") as f_in:
            with gzip.open(self.path + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        with open(self.path, "rb") as f_in:
            with bz2.open(self.path + ".bz2", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        with open(self.path + '.iso-8859-1', 'wb') as f:
            f.write(self.text.encode('iso-8859-1'))
        self.from_file = Editor(self.path)
        self.from_file_iso = Editor(self.path, encoding='iso-8859-1')
        self.from_gzip = Editor(self.path + ".gz")
        self.from_bz2 = Editor(self.path + ".bz2")
        self.from_stream = Editor(StringIO(self.text))
        self.from_string = Editor(self.text)
        self.from_lines = Editor(self.text.splitlines())
        self.from_ed = Editor(self.from_file)

    def tearDown(self):
        """Remove the temporary files generated by the test."""
        os.remove(self.path)
        os.remove(self.path + ".gz")
        os.remove(self.path + ".bz2")
        os.remove(self.path + ".iso-8859-1")
        shutil.rmtree(self.dirpath)

    def test_all_lines_read_correctly(self):
        """Check that lines are equivalent."""
        self.assertListEqual(self.from_file.lines, self.from_file_iso.lines)
        self.assertIsNot(self.from_file.lines, self.from_file_iso.lines)
        self.assertListEqual(self.from_file.lines, self.from_gzip.lines)
        self.assertIsNot(self.from_file.lines, self.from_gzip.lines)
        self.assertListEqual(self.from_file.lines, self.from_bz2.lines)
        self.assertIsNot(self.from_file.lines, self.from_bz2.lines)
        self.assertListEqual(self.from_file.lines, self.from_stream.lines)
        self.assertIsNot(self.from_file.lines, self.from_stream.lines)
        self.assertListEqual(self.from_file.lines, self.from_string.lines)
        self.assertIsNot(self.from_file.lines, self.from_string.lines)

    def test_str_len(self):
        """Test string, length."""
        self.assertEqual(self.text, str(self.from_file))
        self.assertEqual(len(self.from_file), len(self.text.splitlines()))

    def test_repr(self):
        """
        Test that the repr, which has a slightly complex algo, returns a string.
        """
        s = repr(Editor([str(i) + "\n" for i in range(100)]))
        self.assertIsInstance(s, str)
        s = repr(self.from_file)
        self.assertIsInstance(s, str)

    def test_setgetdel(self):
        """Test setting, getting, deleting, and contains methods."""
        old = self.from_file[0]
        self.assertIn(str(old), str(self.from_file))
        self.from_file[0] = "new"
        self.assertIn("new", str(self.from_file))
        del self.from_file[0]
        self.assertNotIn("new", str(self.from_file))
        self.from_file[0] = old

    def test_copy(self):
        """Test that copy correctly copies the lines."""
        cp = self.from_file.copy()
        self.assertListEqual(cp.lines, self.from_file.lines)
        self.assertIsNot(cp.lines, self.from_file.lines)
        self.assertIsNot(cp, self.from_file)

    def test_write(self):
        """Test :func:`~exa.editor.write_file`."""
        fp = self.path + ".test"
        self.from_file.write(fp)
        with open(fp, "r") as f:
            text = f.read()
        self.assertEqual(text, str(self.from_file))
        os.remove(fp)

    def test_format(self):
        """Test the editor's format function."""
        fmttxt = self.text.format(tmp="new")
        fmted = str(self.from_file.format(tmp="new"))
        self.assertEqual(fmttxt, fmted)
        self.from_file.format(tmp="new", inplace=True)
        self.assertEqual(fmttxt, str(self.from_file))
        self.assertIs(self.from_file.format(), self.from_file)

    def test_iter(self):
        """Test editor iteration."""
        lines = [line for line in self.from_file_iso]
        self.assertListEqual(lines, self.text.splitlines())

    def test_contains(self):
        """Test 'in' checks on editors."""
        self.assertIn("text", self.from_file)
        self.assertNotIn(0, self.from_file)

    def test_getitem(self):
        """Test line getting."""
        slce = self.from_file_iso[0]
        self.assertEqual(str(slce), self.text.splitlines()[0])
        self.assertIsInstance(slce, Editor)
        slce = self.from_file_iso[(0, 1)]
        self.assertEqual(str(slce), self.text)
        self.assertIsInstance(slce, Editor)

    def test_init_type_error(self):
        """Test init raising type error."""
        with self.assertRaises(TypeError):
            Editor(Editor)

    def test_find(self):
        """Test line by line searching."""
        found = self.from_file_iso.format(tmp="test").find("test")
        self.assertEqual(len(found), 1)
        self.assertEqual(len(found[0]), 2)
        self.assertEqual(found[0][0].num, 0)
        self.assertEqual(found[0][1].num, 1)

#!/usr/bin/env python3
"""
Unit tests for rating_parser module.
Tests the regex pattern against various markdown and formatting styles.
"""

import unittest
from rating_parser import parse_rating, categorize_quality


class TestParseRating(unittest.TestCase):
    """Test cases for parse_rating function."""
    
    def test_plain_format(self):
        """Test plain RATING: format."""
        self.assertEqual(parse_rating('RATING: 6'), 6)
        self.assertEqual(parse_rating('RATING: 10'), 10)
        self.assertEqual(parse_rating('RATING: 1'), 1)
    
    def test_with_newlines(self):
        """Test RATING with various newline formats."""
        self.assertEqual(parse_rating('RATING:\n6'), 6)
        self.assertEqual(parse_rating('RATING:\r\n6'), 6)
        self.assertEqual(parse_rating('RATING:\n\n\n8'), 8)
        self.assertEqual(parse_rating('RATING\n:\n8'), 8)
    
    def test_bold_markdown(self):
        """Test bold markdown formatting with asterisks."""
        self.assertEqual(parse_rating('**RATING:** 8/10'), 8)
        self.assertEqual(parse_rating('**RATING:**\n\n8 / 10'), 8)
        self.assertEqual(parse_rating('*** RATING: *** 6'), 6)
    
    def test_header_markdown(self):
        """Test markdown headers."""
        self.assertEqual(parse_rating('## RATING: 7'), 7)
        self.assertEqual(parse_rating('### RATING:\n\n9'), 9)
        self.assertEqual(parse_rating('###RATING:7'), 7)
    
    def test_combined_markdown(self):
        """Test combined markdown formatting (headers + bold)."""
        self.assertEqual(parse_rating('## **RATING:**\n7/10'), 7)
    
    def test_spacing_variations(self):
        """Test various spacing patterns."""
        self.assertEqual(parse_rating('RATING : 5'), 5)
        self.assertEqual(parse_rating('RATING  :  4'), 4)
        self.assertEqual(parse_rating('RATING:8/10'), 8)
        self.assertEqual(parse_rating('  RATING: 5  '), 5)
    
    def test_with_slash_ten(self):
        """Test ratings with /10 suffix and various spacing."""
        self.assertEqual(parse_rating('RATING: 8/10'), 8)
        self.assertEqual(parse_rating('RATING: 8 /10'), 8)
        self.assertEqual(parse_rating('RATING: 9/ 10'), 9)
        self.assertEqual(parse_rating('RATING: 7 / 10'), 7)
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        self.assertEqual(parse_rating('rating: 6'), 6)
        self.assertEqual(parse_rating('Rating: 7'), 7)
        self.assertEqual(parse_rating('RATING: 8'), 8)
    
    def test_full_evaluation_text(self):
        """Test with full evaluation text containing summary and reasoning."""
        full_text = """
        SUMMARY:
        This is a blog post summary.
        
        RATING: 6
        
        REASONING:
        This blog post is average quality.
        """
        self.assertEqual(parse_rating(full_text), 6)
    
    def test_invalid_ratings(self):
        """Test that invalid ratings return None."""
        self.assertIsNone(parse_rating('RATING: 0'))
        self.assertIsNone(parse_rating('RATING: 11'))
        self.assertIsNone(parse_rating('RATING: 15'))
        self.assertIsNone(parse_rating('RATING: -5'))
    
    def test_no_rating_found(self):
        """Test that missing ratings return None."""
        self.assertIsNone(parse_rating('This text has no rating'))
        self.assertIsNone(parse_rating('RATING:'))
        self.assertIsNone(parse_rating('SCORE: 8'))
    
    def test_boundary_values(self):
        """Test boundary values (1 and 10)."""
        self.assertEqual(parse_rating('RATING: 1'), 1)
        self.assertEqual(parse_rating('RATING: 10'), 10)
        self.assertEqual(parse_rating('RATING: 1/10'), 1)
        self.assertEqual(parse_rating('RATING: 10/10'), 10)


class TestCategorizeQuality(unittest.TestCase):
    """Test cases for categorize_quality function."""
    
    def test_high_quality(self):
        """Test high quality ratings (8-10)."""
        self.assertEqual(categorize_quality(8), 'high')
        self.assertEqual(categorize_quality(9), 'high')
        self.assertEqual(categorize_quality(10), 'high')
    
    def test_mid_quality(self):
        """Test mid quality ratings (6-7)."""
        self.assertEqual(categorize_quality(6), 'mid')
        self.assertEqual(categorize_quality(7), 'mid')
    
    def test_low_quality(self):
        """Test low quality ratings (1-5)."""
        self.assertEqual(categorize_quality(1), 'low')
        self.assertEqual(categorize_quality(2), 'low')
        self.assertEqual(categorize_quality(3), 'low')
        self.assertEqual(categorize_quality(4), 'low')
        self.assertEqual(categorize_quality(5), 'low')
    
    def test_boundary_transitions(self):
        """Test boundary values between categories."""
        self.assertEqual(categorize_quality(5), 'low')
        self.assertEqual(categorize_quality(6), 'mid')
        self.assertEqual(categorize_quality(7), 'mid')
        self.assertEqual(categorize_quality(8), 'high')


if __name__ == '__main__':
    unittest.main()

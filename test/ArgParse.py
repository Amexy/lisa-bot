import unittest

from commands.cogs.Cards import FilteredArguments, filterArguments, Character, Rarity, Attribute


class ArgParse(unittest.TestCase):
    def test_wrong_name(self):
        result = filterArguments("foo2")
        self.assertIsNone(result.success)
        self.assertIsNotNone(result.failure)

    def test_card(self):
        result = filterArguments("kokoro")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_alias(self):
        result = filterArguments("Yukinya")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Yukina)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_number(self):
        result = filterArguments("kokoro", "2")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertEqual(success.position, 2)
        self.assertFalse(success.df)
        self.assertFalse(success.last)
        self.assertIsNone(success.title)

    def test_card_number_together(self):
        result = filterArguments("kokoro2")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertFalse(success.last)
        self.assertEqual(success.position, 2)
        self.assertIsNone(success.title)

    def test_card_rarity_number_together(self):
        result = filterArguments("kokoro", "rare4")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Rare)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertFalse(success.last)
        self.assertEqual(success.position, 4)
        self.assertIsNone(success.title)

    def test_card_rarity_number(self):
        result = filterArguments("kokoro", "sr", "8")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Sr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertFalse(success.last)
        self.assertEqual(success.position, 8)
        self.assertIsNone(success.title)

    def test_card_df(self):
        result = filterArguments("kokoro", "df")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertIsNone(success.rarity)
        self.assertIsNone(success.attr)
        self.assertTrue(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_df_attr(self):
        result = filterArguments("kokoro", "df", "happy")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertIsNone(success.rarity)
        self.assertEqual(success.attr, Attribute.Happy)
        self.assertTrue(success.df)
        self.assertFalse(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_last(self):
        result = filterArguments("kokoro", "last")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_last_attr(self):
        result = filterArguments("kokoro", "last", "happy")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertIsNone(success.rarity)
        self.assertEqual(success.attr, Attribute.Happy)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_last_rarity_attr_together(self):
        result = filterArguments("kokoro", "lastsr", "happy")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Sr)
        self.assertEqual(success.attr, Attribute.Happy)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_last_rarity_attr(self):
        result = filterArguments("kokoro", "last", "rare", "happy")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Rare)
        self.assertEqual(success.attr, Attribute.Happy)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_card_last_rarity_attr_misspell(self):
        result = filterArguments("kokoro", "last", "ssr", "hpy")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertEqual(success.char, Character.Kokoro)
        self.assertEqual(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertTrue(success.last)
        self.assertIsNone(success.position)
        self.assertIsNone(success.title)

    def test_title(self):
        result = filterArguments("title", "maritime", "detective")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.success)
        self.assertEqual(type(result.success), FilteredArguments)
        success: FilteredArguments = result.success
        self.assertIsNone(success.char)
        self.assertIsNone(success.rarity, Rarity.Ssr)
        self.assertIsNone(success.attr)
        self.assertFalse(success.df)
        self.assertFalse(success.last)
        self.assertIsNone(success.position)
        self.assertEqual(success.title, "maritime detective")


if __name__ == '__main__':
    unittest.main()

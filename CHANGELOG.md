CHANGELOG
=========

## 2.0.1 (2016/07/19)
- Re-added `.disable_variable_expansion()` as this function was unintentionally deleted.

--------------------

## 2.0.0 (2016/07/19)
- Rewrite of assertion code to split into different classes with objects that can chain together. This should result in tests that are easier to understand.
- Variables in strings are not expanded by default anymore. Use `.enable_variable_expansion()`` to expand variables.
- assert_* functions are deprecated, but can still be used.
- New error_if_property_missing() function will cause the validator to raise an exception if no matching properties were found in a resource.

--------------------

## 1.2.0 (2016/07/14)
- Attempt to calculate a variable value if it is enclosed in `upper()` or `lower()` interpolation functions

--------------------

## 1.1.1 (2016/07/14)
- Fixed bug that caused asserts to throw errors when there were no "resource" configurations present in a terraform project

--------------------

## 1.1 (2016/07/13)
- Addition of new Asserts that validate Variable default values
  - assert_variable_default_value_exists
  - assert_variable_default_value_equals
  - assert_variable_default_value_matches_regex

--------------------

## 1.0 (2016/07/13)
- Initial Release

--------------------

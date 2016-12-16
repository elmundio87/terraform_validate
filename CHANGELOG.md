CHANGELOG
=========

## 2.1.6 (2016/12/16)

- Fix multiline regex - thanks @eredi93

## 2.1.5 (2016/08/01)

- Better string <-> boolean comparison in `should_equal` and `should_not_equal`

## 2.1.4 (2016/07/26)

- No real changes, just a code coverage version bump

--------------------

## 2.1.3 (2016/07/25)

- Fix all error messages to ensure that they provide the correct information. All error messages are now tested.

--------------------

## 2.1.2 (2016/07/22)

- Fix the should_have_properties and should_not_have_properties to work properly when given a string thats not in a list

--------------------

## 2.1.1 (2016/07/22)

- Resource matching done via a string will now work as a regex. Lists passed into `.resource` will work as before.
- Regex matching is more strict, will automatically enclose strings with ^ and $ characters.

--------------------

## 2.1.0 (2016/07/21)

- Updated validation function names
- Fixed boolean:string comparison in `.should_equal()` and `.should_not_equal()`

--------------------

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

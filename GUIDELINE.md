#Style Guidelines
This style guideline may seem draconian, but it is more for my sake than anything else. 

Unless I lay out clear guidelines that aren't easy to change, I'll inevitable use three styles simultaneously.

## General
The most important point here is to follow PEP8 as closely as possible. Such as:

* Indents are 4 spaces per level. FlaskAmp is Python3 based and will break if tabs are used.
* Maximum line length of 79 characters for code, 72 for comments and docstrings. 
* If a few lines here and there run over 79, that's fine however use your best judgement.
* Blank lines:
    * One blank line after each code block (this causes a logical seperation)
    * Two blank lines after a class or function defition.
    * Inside of a class, one blank line between each method.
    * If class variables are created, there are two blank lines between them and __init__
* Use white space to logically break up expressions.

##Docstrings and Comments
Docstrings are for the benefit of the person using your code. Comments are for the person editing your code.

All files must have docstrings. All classes must have docstrings. All functions must have docstrings.

There are, of course, always exceptions. 

* A function or method that is brief (five to ten lines max) may forego docstrings if the logic is clear and it is well named.
* An init method that is purely accepting arguments into the object may forego docstrings.
* Dunder methods like repr, str, and len may forego docstrings.
* Dunder methods like get, set, del require docstrings.
* Other dunder methods like iter and next are left to best judgement if a docstring is required.
* A file that serves only as a namespace for variables and is well named, may forego docstrings.
* A 'pivot' or 'mapper' or 'many_to_many' tables may forego docstrings. These tables and models are defined as primiarly serving as just a many-to-many mapper with no more than two native attributes (TrackPosition, for example is many-to-many mapper that contains `position`, a native attribute).
* A marshmallow schema metaclass may forgo docstrings.

Docstrings should be written in Sphinx compliant rst.

Comments should be used to clarify code in particular. Inline comments are discouraged, but not forbidden.

Code should never be commented out. If it is example code, it belongs in a docstring.

##Exceptions
Python defines *many* exceptions in the standard library. When considering a custom exception, it must subclass at least FlaskAmpError and it must be appropriately vague.

Appropriately vague means that it applies to a particular error but isn't so specific that it can only occur in a single area.

* `TracklistError` is an okay example if it applies to errors originating out of tracklists in general.
* `UserNameTooLongError` is not okay as it is a very specific error.

Exceptions to this rule can be made if absolutely needed. When in doubt, throw FlaskAmpError.

###Raising exceptions
Exceptions are not a stand in for flow control. They purposely disrupt code flow to say, "HEY! Something could go very wrong here."

It is left to best judgement if an exception is more appropriate than an if block.

###Recovering from Exceptions

* If an exception can be recovered from gracefully, then it is okay to attempt to recover. 
* Passing on handling exceptions is fine as long application intregity can be guaranteed.
    * Passing on handling an exception because of a missing audio file is fine, provided no database record was created.
    * Passing on an IntegrityError from the database is not acceptable.
* However, recovery efforts should only run one level deep. There is only one chance to recover.
* Attempting to recover from a recovery should only serve to propagate a more appropriate exception to the log and end user.
* Only attempt to recover from expected edge cases and errors.
    * Expecting a `KeyError` is fine.
    * Expecting `Exception` is not.

###Structuring recoveries

* Code contained in a try block must be as minimal as possible to isolate expected errors.
* Try blocks must always be partnered with an except block.
* An else block is required where code is conditional on the success of a try block.
* A finally block is required when clean up code should be executed regardless of the Try block's success.

###Logging Exceptions
When propagating exceptions to the log, the tendency is towards clarity.

* Exceptions raised in FlaskAmp code must always contain an error message. A bare exception is considered a bug. 
* Exception messages should be brief and descriptive.

###Propagation of Exceptions
When propagating exceptions to end users, the tendency is toward vagueness.  Unless otherwise specified, FlaskAmpError propagates to a generic 500 error.

* A user should be notified that there is an internal server error, but should not necessarily that there was a particular error. 
* A user should be notified that they could not be properly identified, but not necessarily that the email, password, public key or private key was invalid.
* Always propagate an internal error to an appropriate HTTP Status Code.

##Lambdas
Lambdas should be used only for throwaway functions, for example sort keys or SQLAlchemy callables.

If you assign a lambda to a name, consider defining it as an actual function instead.

There can be a case made for assigning a lambda to a name if defining it in the context of a function argument would complicate the logic unnecessarily.

##Imports
* Avoid circular imports whenever possible.
* Imports go at the top of each file, after any file docstrings.
* Imports of whole packages go before specific imports (i.e. import something before from something import thing)
* Imports are divided into groups, each seperated by a blank line:
    * Standard library imports
    * Third party packages (each individual third party library is seperated by a blank line -- except for `import from flask.ext` this is optional, but must be consistent in each module)
    * Relative imports from above
    * Relative imports from the same level

When possible, alphabetize imports.

An exmple:

    import os
    from uuid import uuid4

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    from sqlalchemy.ext.associationproxy import association_proxy

    from ..config import configs
    from . import schemas
    from .utils.factories import create_app

##Naming conventions
* All things must be well named. With few exceptions, a name is descriptive.
* Modules are lowercase and never underscore seperated.
* Functions. variables, class attributes and instance attributes are lowercase and underscore separated.
* Constants are UPPERCASE and underscore separated. Constants should never be overridden.
* Class names are StudlyCapped and never underscore seperated.

There are a few reserved names:
* `q` for methods and functions that require only one query against models. that query must be named q. If you require multiple queries, they must be well named.
* Similarly, if there is one query that takes advantage of Flask-SQLAlchemy's pagination, that actual pagination result must be named `pages`.
* If composing a single data structure for a result, it must be named result. Otherwise, it must be well named.

##Object Guidelines
Attributes and methods are defined in this order and always presumed to be ordered alphabetically. Underscore (`_`) is presumed to come before `a`.

1. Class level attributes
2. __init__ *must* be the first method defined on an object.
3. Other magic methods, if needed, next.
4. @property defined fields
5. Instance methods
6. Class methods
7. Static methods

Use class and static methods sparingly. Python is object oriented, not class oriented.

Similarly, if you define a class that only has `__init__` and a single other method, you have created a function closure. Write it as such. To clarify, this doesn't apply to subclasses that need custom initialization logic.


###Model specific guidelines

Models are a special case they commonly employ many class level attributes and fewer methods.

* Naming: All models are named in StudlyCaps. Tablenames are lowercase, underscored separated.
* __tablename__ is *always* the first class attribute defined on a model.
* `__mapper_args__` and `__table_args__` are defined next if applicable.
* If applicable, models that use the `ReprMixin` and need to define their own fields.
* Columns are defined in this order:
    *  `id` -- Primary key -- this is always an integer surrogate primary key. Yes, I know why I shouldn't use them.
    * `name` -- if applicable, this is always a unique, indexed Unicode field of 32 characters. This should be considered the natural primary key.
    * Unique, single line fields -- things such as email.
    * Non-unique single line fields.
    * Unique, multiline fields.
    * Non-unique multiline fields
    * Declared attribute fields
    * Hybrid properties.
* Where possible, reference other models as strings. If needed, a callable is appropriate. Using the actual class is prohibited.

Declared attributes and hybrid properties supercede `__init__` as the first method defined. This is purely to group all columns in a logical group.

###Schema specific guidelines

* All schemas are named for what they serialize and end with Schema. A Member schema is named MemberSchema.
* Versioned schemas, due to Marshmallow's `class_registry` system, are a sole exception to class naming conventions.
    * Versioned schemas begin with VX_ where X is the current major version of the API.
    * If marshmallow's class_registry system changes to accomodate versioned APIs, this must immediately change.
* All schemas inherit from a BaseSchema class.
* BaseSchema defines areas common to all schemas in it's group. Including the Meta options class.
* Schemas propagated to the API must map directly to defined data models. Non-compliant schemas are considered a bug.

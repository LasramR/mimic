# Mimic

Mimic is a CLI tool that allows you to easily create project templates (**mimic templates**) and clone them, prompting for variables and running hooks to generate your project (a **mimic**).

Mimic templates are primarily git-based (ie stored in a git repository), but they can also be stored in a local folder.

By using mimic, you ...

## Table of content

1. [Installation](#installation) 
    1. [Prerequisites](#prerequisites)
    1. [Ubuntu, Debian](#ubuntu-debian)
    1. [Windows](#windows)
1. [Command line options](#command-line-options)
1. [.mimic.json schema references](#mimicjson-schema-references)
    1. [git property](#git-property)
    1. [template property](#git-property)
    1. [hooks property](#git-property)
1. [Usage](#usage)
    1. [Creating a mimic template](#creating-a-mimic-template)
        1. [Initialization](#initialization)
        1. [Using variables in your mimic template](#using-variables-in-your-mimic-template)
            1. [Defining a variable](#defining-a-variable)
            1. [How to use a variable](#how-to-use-a-variable)
            1. [Escaping variables](#escaping-variables)
        1. [Debugging your mimic template with mimic lint](#debugging-your-mimic-template-with-mimic-lint)
        1. [Previewing your mimic template with mimic preview](#previewing-your-mimic-template-with-mimic-preview)
        1. [Using hooks in your mimic template](#using-hooks-in-your-mimic-template)
        1. [Integrating git in your mimic template](#integrating-git-in-your-mimic-template)
    1. [Cloning a mimic template](#cloning-a-mimic-template)
    1. [Using mimic aliases](#using-mimic-aliases)
1. [Exemple](#exemple)
1. [Roadmap](#roadmap)

## [Installation](#installation)

### [Prerequisites](#prerequisites)

### [Ubuntu, Debian](#ubuntu-debian)

### [Windows](#windows)

## [Command line options](#command-line-options)

## [.mimic.json schema references](#mimicjson-schema-references)

### [git property](#git-property)

### [template property](#git-property)

### [hooks property](#git-property)

## [Usage](#usage)

### [Creating a mimic template](#creating-a-mimic-template)

#### [Initialization](#initialization)

To create a **mimic template** (ie a folder structure containing files that represents a project), simply run :

```sh
mimic init
```

This will create a file named `.mimic.json` in your current folder.

This file is the core of mimic, it is used to :
* define variables in your mimic-template
* define hooks to trigger when generating a **mimic** (ie a folder structure that has been processed by the mimic CLI) from your mimic template
* integrate git in your mimic

The following sections covers the usage of the `.mimic.json` file.

#### [Using variables in your mimic template](#using-variables-in-your-mimic-template)

First of all, let's clarify what do we call a *variable* :

```md
A variable is a name defined in the `.mimic.json`. 
When generating a mimic from a template, the user will be prompted to indicate which value to associate with the variable.
This value will be used by the mimic CLI to perform substitution of the variable name by the user.
```

Ok, but where can we use variables :
* inside a file (ie the file content)
* as a file name
* as a directory name
* as a hook command (see [Hooks](#using-hooks-in-your-mimic-template))

So, let's define a variable. As explained, to define a variable in your template your must edit your `.mimic.json` file.

##### [Defining a variable](#defining-a-variable)

Go to your `.mimic.json` file and look for the *template* property :

```json
// .mimic.json
{
  "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json",
  ...
  "template": {
    "variables": {}
  }
  ...
}
```

The template property should contain a *variables* property, if not, add a property *variables* in the *template* property.

To define a variable, you must add a property with the name of your variable in the *variables* property :

```json
// .mimic.json
{
  "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json",
  ...
  "template": {
    "variables": {
      "my_var": {}
    }
  }
  ...
}
```

In the example above, we defined a variable named *my_var*.

To finish defining our variable we must also specify a *type* property :

```json
// .mimic.json
{
  "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json",
  ...
  "template": {
    "variables": {
      "my_var": {
        "type": "string"
      }
    }
  }
  ...
}
```

In the example above, we specified that our variable *my_var* is of type *string*. The *type* property is used to constrain the acceptable value of variable when prompted to the user.

You can define as much variables as you want in your mimic template. There are plenty of type that can be used to constrains your variable and there are additionnal properties that can be used to specify your variables. Refer to [template property](#template-property) to learn more about variables.

Now that we have defined a variable, let's use it.

##### [How to use a variable](#how-to-use-a-variable)

To use a variable, you must use the mustache (`{{ _ }}`) syntax with the name of your variable (in this example, `{{ my _var }}`). When cloning your mimic template, the mimic CLI will look up for each object (ie file, folder) in your mimic template that is suffixed with `.mimict` or `.mt`.

When the mimic CLI find an object (ie file, folder) that is suffixed with `.mimict` or `.mt`, it will :
* look in the file name and replace each mustache (`{{ _ }}`) it will find with their corresponding variable value.
* look in the directory name and replace each mustache as well
* look in the file content (if processing a file) and replace each mustache as well
* for each object that the mimic CLI processed, it will removed the `.mimict` or `.mit` suffix

Let's illustrate with an example :

This our mimic template structure :

```
my-mimic-template/
├─ .mimic.json/
├─ {{ my_var }}.mt/
│  ├─ {{ my_var }}_lib.ts
├─ biome.json
├─ main.ts
├─ package.json.mt
```

And this is the content of the `package.json.mt` file :

```json
// package.json.mt
{
  "name": "my-awesome-package",
  "version": "1.0.0",
  "description": "{{ my_var }}"
}
```

If we [clone](#cloning-a-mimic-template) the mimic template and set the value of *my_var* to "helloworld", then, the mimic template structure will become :

```
my-mimic-template/
├─ helloworld/
│  ├─ helloworld_lib.ts
├─ biome.json
├─ main.ts
├─ package.json
```

Notice that the `.mimic.json` has been removed, all file names and folder names suffixed with .mt have been processed. And the content of the `package.json` file will become :

```json
// package.json
{
  "name": "my-awesome-package",
  "version": "1.0.0",
  "description": "helloworld"
}
```

But, what if we didn't defined the variable *my_var* in `.mimic.json` file ?

Then, when [cloning](#cloning-a-mimic-template) the mimic template, all occurences of `{{ my_var }}` will be replaced with empty string!

This can be problematic, especially when you make small typos such as "myvar" and "my_var". The following sections :

* [Debugging your mimic template with mimic lint](#debugging-your-mimic-template-with-mimic-lint)
* [Previewing your mimic template with mimic preview](#previewing-your-mimic-template-with-mimic-preview)

Will explain you how to detect errors and dangling variables in your projects + it will explain you how to preview what will be generated from your mimic template.

##### [Escaping variables](#escaping-variables)

Let's say I have the following `package.json.mt` file : 

```json
// package.json.mt
{
  "name": "my-awesome-package",
  "version": "1.0.0",
  "description": "{{ my_var }}"
}
```

And that for some reason, I actually want the value of *description* to be "{{ my_var }}" (ie no substitution).

If I don't want my `package.json.mt` file to be processed by the mimic CLI, I can simply rename it to `package.json`.

But, what if I need to use a variable as my package *name* property value :

```json
{
  "name": "{{ package_name }}",
  "version": "1.0.0",
  "description": "{{ my_var }}"
}
```

If we don't define the variable *my_var*, then the mimic CLI will replace it with an empty string. 

We could define the variable *my_var*, but we will need to define its value as "{{ my_var }}" to keep it as it is. This will work (besides being annoying) but that mean that *my_var* cannot be used elsewhere, otherwise it will be also replaced with "{{ my_var }}".

The solution to this problem is to **escape** the mustache by mustaching the mustache :

```
{{{{ my_var }}}}
```

When the mimic CLI encounter a mustached mustache, it will replaced it with the inner mustaches :

```
{{{{ my_var }}}}
```

will become :

```
{{ my_var }}
```

That's it about variables.

Note: I am considering adding a command `mimic escape` to automatically escape an entire file, this can be usefull when templating mustache templates

#### [Debugging your mimic template with mimic lint](#debugging-your-mimic-template-with-mimic-lint)

#### [Previewing your mimic template with mimic preview](#previewing-your-mimic-template-with-mimic-preview)

#### [Using hooks in your mimic template](#using-hooks-in-your-mimic-template)

#### [Integrating git in your mimic template](#integrating-git-in-your-mimic-template)

### [Cloning a mimic template](#cloning-a-mimic-template)

### [Using mimic aliases](#using-mimic-aliases)

## [Exemple](#exemple)

## [Roadmap](#roadmap)

* Proper testing
* Mimic Bank (ie, one git repository / folder = multiple mimic templates)
* Better choice prompt
* Replace boolean prompt with Y/n
* Simple conditionnal rendering (For loops and other advanced mecanism are not planned)

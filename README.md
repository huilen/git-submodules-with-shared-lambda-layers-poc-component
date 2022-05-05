# Introduction

This is a PoC to show how to use Git submodules with Lambda layers.

## Project structure

This repository represents the standard component of the system. Its structure is the same that you will find in each other component of the system:
```
component
├── shared
│   ├── README.md
│   └── python
│       └── classes.py
└── component files
```

Where *shared* is a Git submodule pointing to the repository *git-submodules-with-shared-lambda-layers-poc-shared*

In submodule *shared* you will find shared classes, that are supposed to be used by all components accross the application.

At root level you will find a *sam* project for a sample serverless application with a single endpoint pointing to a Lambda function.

In *template.yml* you will note the following:
- There is a layer declaration, referring the code inside *shared* submodule.
- There is a function declaration that is used as an example of application endpoint.
- The function has a reference to the layer, so the packages of the layer will be available in the function environment.

In *app.py* you will see that there is an `import classes`, which is importing shared classes from shared. This will work thanks to the layer reference.

## Why we use Git submodules

Working with shared repositories for a project using Lambda functions is painful without Git submodules. For example, if we are working on a component and we need to make a change in the shared code, then it is necessary to deploy a new version of the shared layer to be able to refer the new version from the sam template of the component.

With this Git submodules strategy we can test changes in shared code locally when working on another module without need to deploy anything.

### How to use Git submodules

Git submodules can be misused, if they are not understood correctly, and every developer must be careful when using them.

One important thing that one have to understand about Git submodules is that they are standalone. Actually, they are just Git repositories, and you can clone them independently and work with them as you work with any other Git repository.

A Git submodule becomes a Git submodule only inside another repository (let's call it "super" repository) which declares a normal repository as a Git submodule.

You should never expect that a commit in the super repository should cause a commit in the submodules. Since they are independent each other, you need to commit in each submodule. The only thing that the super repository has is just a reference to the repositories of the submodules, but they are independent repositories.

Let's say we have three repositories: A, B and C.

They are all just common and plain repositories, there is no magic there.

Now, we can make A refer to B and C as submodules, doing this:

```
git clone <Git url for cloning repository A> A
cd A
git submodule add <Git url for cloning repository B> B
git submodule add <Git url for cloning repository C> C
git commit -m "Adding submodules B and C"
git push origin main
```

You will see two directories inside A repository: B and C. And in these directories you will see all the files from B and C repositories.

But B and C keep working as normal repositories, and you can even clone them independently as always. But now A has a reference to them.

Right now A is pointing to last version of main branch in repositories B and C. Actually, if you clone A again, you will see under B and C directories all the files as they are in the last version of main branch of these repositories.

Now, let's say you push a new file into repository B. Will you see this file automatically in repository A under B directory?

The answer is NO. This is because A is still pointing to the previous version of B submodule.

If you want to update to the new version you will need to do the following:

```
cd shared/
git pull origin main
cd ..
git add shared
git commit -m "Update reference to B repository"
git push origin main
```

Only then A will be pointing to the new version of B.

Also, keep in mind that whenever you clone the super repository you
will need to initialize submodules, thus:

```
git clone <super repository>
git submodule update --init <submodule>
```

Or you will see the submodule empty.

### How to use branches with submodules

Let's say we have two branches for the super repository: main and
dev. We should have also these two branches for each submodule too.

In this case we have only one submodule called "shared".

#### How to commit a new feature into submodule

Let's see how we would commit a new feature into shared submodule:
```
git checkout dev # move to dev branch in super repository
cd shared/
git checkout dev # move to dev branch in shared repository
echo something > feature.txt
git add feature.txt
git commit -m "add new feature"
cd ..
git add shared
git commit -m "update reference of shared submodule"
git push origin dev
```

That would be all. Now, have in mind that whenever you change to
another branch (with git checkout <branch>) you should always update
the submodule:

```
git checkout main
git submodule update shared
```

If you don't do the update, in this case you will see the contents of
the dev branch instead of the contents of main branch.

#### How to commit a hot fix

Let's say we have to commit a hot fix into main branch. We would do
the following:

```
git checkout main # move to main branch in super repository
cd shared/
git checkout main # move to main branch in shared repository
echo hotfix > hotfix.txt # create hot fix
git add hotfix.txt
git commit -m "add hotfix"
git push origin main
git add shared
git commit -m "update reference of shared submodule"
git push origin main
```

You already have the hot fix in main branch, now you need to merge
main back into dev branch so you include your hot fix there too. In
order to do this you will need to merge first the submodule, and then
the super repository:

```
git checkout dev
cd shared/
git checkout dev
git merge main
git commit
git push origin main
cd ..
git add shared
git commit -m "update reference of shared submodule"
git push origin main
```

#### ATENTION

If you make a change into a submodule, you should never commit in the super repository without commiting and pushing the change first in the submodule.

If you commit something in a submodule, without making a push, and then you do a "git add" of the submodule in the super repository and commit and push in the super repository, you will end with a reference in the super repository to a submodule version that doesn't exist in the remote (because you have never pushed it).

Remember, Git submodules are standalone repositories, and you need to handle them separetely. In the super repository you only have a reference to the repositories of the submodules.

# How to use it

## Requirements

- Python 3.9.7
- Sam 1.40.1

## How to run it

```
sam local invoke HelloWorldFunction
```

This will invoke the function in *component* locally, and you will see that it prints the value that is coming from *shared* layer.

## Changing shared code

Let's say you are working on *component*, and you need to make a change in *shared*. You just need to make the change locally and nothing else. No need to deploy anything.

## Working with Git submodules

1. Being in the *component* repository, make the changes you want under *component* and under *shared* submodule.
2. Commit and push inside the submodule:
```
cd shared/
git commit -m "some change in shared"
git push origin main
```
3. Update, add, commit and push from the *component* repository.
```
cd ..
git submodule update shared
git commit -m "update reference to shared submodule"
git push origin main
```

NOTE: It is extremely important that you follow this order strictly: pushing first in the *shared* submodule; and then adding, commiting and pushing in the *component* repository.

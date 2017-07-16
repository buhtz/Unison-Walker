# This repo is no out-dated and migrated to GitLab. Please use the [repository on GitLab](https://gitlab.com/buhtz/Unison-Walker).

# Unison-Walker
A helper script for the file syncronization software [Unison](https://www.cis.upenn.edu/~bcpierce/unison). It take care of unneeded backup-files created but never deleted by Unison.
# Details
## The problem
*Unison* can be setup to [create a backup file](https://www.cis.upenn.edu/~bcpierce/unison/download/releases/stable/unison-manual.html#backups) (hereinafter called *bak-file*) when a file is modified or deleted while a synchronization process. But the problem is it doesn't take care of the deletion of that file. When you use *Unison* over a huge periode of time your hard drive will fill up with hidden bak-files without any control.
## The solution
This script looks for *bak-files* which haven't a corrosponding existing original file anymore. It also consider about the age of that files. All files found will be shown.

**Remember**: This scrip will never touch nor delete the found files. It only show their names on the standard output.
# Limitations
Currently this script and the concept behind it only work when *Unison* use a central backup location (`backuploc=central`).
# Future
There is a [discussion](http://lists.seas.upenn.edu/pipermail/unison-hackers/2015-September/001873.html) on the *Unison-hackers* mailinglist about implementing a feauter like this. In that case this script would be obsolete of course.
# Licence
See the [LICENSE](LICENSE) file for details.

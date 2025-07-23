# GPFS SNIPPETS

- See Also: [GPFS Tools Repo](https://github.com/lordachoo/gpfsTools)

## NUKE GPFS FS (ALL)

```bash
## Nuke entire filesystem .. 
# Nuke client side pids/shell connections that are using gpfs
$ for i in `lsof /mmfs1 | grep -v COMMAND | awk '{print $2}'`; do kill $i; done
# Check
$ mmlsmount mmfs1 -L
# Unmount them all
$ mmumount all -a
# Delete Filesystem
$ mmdelfs mmfs1
# Nuke NSD
$ for i in `mmlsnsd | grep -v "\-\-\-\-" | grep  -v "File system" | awk '{print $3}'`; do mmdelnsd $i; done
```

## POLICY EXAMPLES

### DELETE FILES BY PATH

- Good for performant deletions

```
## NO WEIGHTS, Might need to run several times as files with longer paths are needed to be deleted first to avoid 'directory isnt empty' errors
RULE 'rule_name' DELETE
    DIRECTORIES_PLUS 
    WHERE PATH_NAME LIKE '/mmfs1/fileset/dir/%'

## WITH WEIGHTS
RULE 'rule_name' DELETE 
    DIRECTORIES_PLUS 
	WEIGHT(Length(PATH_NAME))
    WHERE PATH_NAME LIKE '/mmfs1/fileset/dir/%'
```

### Hydrate by ATIME

```
include(/mmfs1/.arcapix/policies/pixit_excludes.m4)

/* Define the target pool for recall */
define(targetpool,'sas1')

/* Define the target fileset for recall */
define(targetfileset,'sas1-scripts')

/* Define the target path for recall */
define(targetpath,'/mmfs1/data/scripts/')

RULE EXTERNAL POOL 'NGENEA_DEFAULT'
    EXEC '/var/mmfs/etc/mmpolicyExec-ngenea-hsm'
    OPTS '-v1 --log-target=syslog'
    ESCAPE '%'

RULE 'Hydrate 30 Days Access Time'
    MIGRATE FROM POOL 'NGENEA_DEFAULT' TO POOL targetpool
    WHERE PATH_NAME LIKE CONCAT(targetpath,'%')
    AND ((DAYS(CURRENT_TIMESTAMP) - DAYS(ACCESS_TIME)) <= 30)
    AND CountSubstr(MISC_ATTRIBUTES,'V')>0
```

### MIGRATE EXAMPLE

```
/* Example Policies for migration with function explanations, etc 
**    Andrew Nelson - 2024 */

/* EXAMPLE EXCLUDE LIST - Example usage clause : " AND NOT(exclude_list) " */
    define(
      exclude_list,
       (
         PATH_NAME LIKE '%/.ctdb/%'  
         OR PATH_NAME LIKE '%/excludeMe/%'
        ) 
     )

/* MIGRATE ALL .DAT FILES TO different pool */
RULE 'dat-files-pool-migrate-sas1-to-sas2'
    MIGRATE 
    FROM POOL 'sas1' 
    TO POOL 'sas2' 
    WHERE 
    UPPER(name) like '%.DAT'
    AND NOT (exclude_list)
```

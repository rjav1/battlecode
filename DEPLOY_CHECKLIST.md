# MANDATORY DEPLOY CHECKLIST

Before EVERY submission to ladder, run these tests. Takes 5 minutes. Prevents catastrophic regressions.

## Step 1: Save the current live version
```bash
cp bots/buzzing/main.py bots/buzzing_prev/main.py
```

## Step 2: Run regression tests (must win 4/5)
```bash
cambc.bat run buzzing buzzing_prev default_medium1
cambc.bat run buzzing buzzing_prev hourglass
cambc.bat run buzzing buzzing_prev landscape
cambc.bat run buzzing buzzing_prev corridors
cambc.bat run buzzing buzzing_prev settlement
```

## Step 3: Check Ti mined (must be > 10,000 on medium+ maps)
Look at the output. If "0 mined" appears, DO NOT SUBMIT.

## Step 4: Self-play crash test
```bash
cambc.bat run buzzing buzzing default_medium1
```
Must not crash.

## ONLY if all 4 steps pass: submit
```bash
cambc.bat submit bots/buzzing/
```

## IF ANY STEP FAILS: DO NOT SUBMIT. Fix first.

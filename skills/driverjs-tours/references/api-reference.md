# Driver.js API Reference

Methods on the instances returned by `driver()` and `hints()`. Each factory call returns an independent instance — configuration, steps, and state never overlap between instances.

## Driver instance — `driver()`

```js
import { driver } from "driver.js";
import "driver.js/dist/driver.css";

const driverObj = driver({ /* Config — see references/configuration.md */ });
```

### Start / navigate
```js
driverObj.drive();            // start the tour at step 0
driverObj.drive(4);           // start at step index 4

driverObj.moveNext();         // go to next step
driverObj.movePrevious();     // go to previous step
driverObj.moveTo(4);          // jump to step index 4

driverObj.hasNextStep();      // boolean
driverObj.hasPreviousStep();  // boolean
driverObj.isFirstStep();      // boolean
driverObj.isLastStep();       // boolean
```

### Introspect
```js
driverObj.getActiveIndex();     // number — current step index
driverObj.getActiveStep();      // DriveStep — current step config
driverObj.getPreviousStep();    // DriveStep
driverObj.getNextStep();        // DriveStep
driverObj.getActiveElement();   // HTMLElement — current highlighted element
driverObj.getPreviousElement(); // HTMLElement
driverObj.getState();           // State object (see configuration.md)
driverObj.isActive();           // boolean — tour or highlight currently active
```

### Configure at runtime
```js
driverObj.getConfig();
driverObj.setConfig({ /* Config */ });   // change options on the fly
driverObj.setSteps([ /* DriveStep[] */ ]); // replace the steps array
```

### Highlight a single element
```js
driverObj.highlight({
  element: "#some-element",
  popover: { title: "Title", description: "Description" },
}); // no buttons by default when highlighting a single element
```

### Layout & teardown
```js
driverObj.refresh();   // recalculate and redraw after layout/scroll/resize changes
driverObj.destroy();   // remove overlay/popover and clean up listeners
```

**Common patterns:**
- Call `refresh()` after the highlighted element moves or resizes (e.g. images load, accordion opens) so the cutout and popover reposition.
- Always keep the `driverObj` reference alive for the tour's lifetime; losing it means you can't `destroy()` and the overlay can get stuck.

---

## Hints instance — `hints()`

```js
import { hints } from "driver.js/hints";
import "driver.js/dist/hints.css";

const productHints = hints({ /* HintsConfig — see references/configuration.md */ });
```

### Mount / unmount beacons
```js
productHints.show();   // mount the beacons. Calling again picks up hints whose elements have since appeared.
productHints.hide();   // remove beacons + listeners; show() brings them back
productHints.isVisible(); // boolean — whether beacons are currently shown
```

### Open / close / dismiss (addressed by `id`, or array index when no id)
```js
productHints.open("export");    // open a hint's popover programmatically
productHints.close();           // close the open popover, keep its beacon
productHints.dismiss("export"); // remove the hint's beacon and fire onDismiss
productHints.restore("export"); // bring a dismissed hint back
productHints.restoreAll();      // bring every dismissed hint back
```

### Manage / introspect
```js
productHints.setHints([ /* DriverHint[] */ ]); // replace hints; RESETS dismissals
productHints.getHints();   // configured hints
productHints.getActive();  // the hint whose popover is open, if any
productHints.refresh();    // reposition beacons, open popover, and overlay after layout changes
```

**Persisting dismissals:** hints don't remember dismissals across page loads on their own. Give each hint a stable `id`, persist dismissed ids (e.g. to `localStorage`) in `onDismiss`, and on the next `show()` call `dismiss(id)` for each already-seen hint (or filter them out of the `hints` array before constructing).

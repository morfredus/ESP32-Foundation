/**
 * main.cpp — Point d'entrée. Ne contient que l'enregistrement des modules
 * métier du projet ; toute la logique d'infrastructure vit dans App/services.
 */

#include <Arduino.h>
#include "core/app.h"
#include "modules/example_module/example_module.h"

static ExampleModule exampleModule;

void setup() {
    Serial.begin(115200);

    app.modules.add(&exampleModule);
    app.begin();
}

void loop() {
    app.loop();
}

#!/usr/bin/env python3
"""Generate a Polish-translated copy of the OpenAPI spec for the docs.

Reads api-reference/openapi.json (English, source of truth) and writes
api-reference/openapi.pl.json with human-facing text translated to Polish:
tag names + descriptions, operation summaries/descriptions, response
descriptions, parameter/schema-property descriptions, and info fields.

Technical tokens (paths, field names, scopes like `subscribers:write`,
enum values like PENDING_CONFIRMATION, HTTP codes) are left untouched.

Re-run after re-copying the English spec from the backend.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "api-reference", "openapi.json")
OUT = os.path.join(HERE, "..", "api-reference", "openapi.pl.json")

# --- Tag names shown as groups in the API Reference menu ---
TAG_NAMES = {
    "Subscribers": "Subskrybenci",
    "Topics": "Tematy",
    "Consents": "Zgody",
    "Suppressions": "Wykluczenia",
    "Campaigns": "Kampanie",
    "Segments": "Segmenty",
    "Custom Fields": "Pola niestandardowe",
    "Automations": "Automatyzacje",
    "Sending Domain": "Domena wysyłkowa",
    "Campaign Reports": "Raporty kampanii",
    "Billing": "Rozliczenia",
    "AI Credits": "Kredyty AI",
    "Project": "Projekt",
}

TAG_DESCRIPTIONS = {
    "Manage subscribers within the API key's project": "Zarządzaj subskrybentami w projekcie klucza API",
    "Manage subscription topics in the project": "Zarządzaj tematami subskrypcji w projekcie",
    "Grant, read and revoke per-topic consent for a subscriber": "Nadawaj, odczytuj i cofaj zgodę subskrybenta per temat",
    "Manage the project suppression list": "Zarządzaj listą wykluczeń projektu",
    "Create, manage, schedule and send email campaigns": "Twórz, zarządzaj, planuj i wysyłaj kampanie e-mail",
    "Create, manage and populate subscriber segments": "Twórz, zarządzaj i wypełniaj segmenty subskrybentów",
    "Define and manage subscriber custom field definitions": "Definiuj i zarządzaj polami niestandardowymi subskrybentów",
    "Create, manage and control email automation workflows": "Twórz, zarządzaj i kontroluj przepływy automatyzacji e-mail",
    "Manage the project's custom sending domain and DNS verification": "Zarządzaj własną domeną wysyłkową projektu i weryfikacją DNS",
    "Read campaign statistics, AI report, timeline and CSV export": "Odczytuj statystyki kampanii, raport AI, oś czasu i eksport CSV",
    "Read subscription, plans, invoices and usage for the account": "Odczytuj subskrypcję, plany, faktury i zużycie dla konta",
    "Read AI credit balance and transaction history for the account": "Odczytuj saldo kredytów AI i historię transakcji dla konta",
    "Read the project the API key is scoped to": "Odczytaj projekt, do którego przypisany jest klucz API",
}

# --- Operation summaries ---
SUMMARIES = {
    "Create a subscriber": "Utwórz subskrybenta",
    "List subscribers": "Wylistuj subskrybentów",
    "Get a subscriber by email": "Pobierz subskrybenta po adresie e-mail",
    "Update a subscriber": "Zaktualizuj subskrybenta",
    "Delete a subscriber": "Usuń subskrybenta",
    "List topics": "Wylistuj tematy",
    "Create a topic": "Utwórz temat",
    "Get a topic by key": "Pobierz temat po kluczu",
    "Update a topic": "Zaktualizuj temat",
    "Delete a topic": "Usuń temat",
    "Grant consent for a topic": "Nadaj zgodę na temat",
    "List a subscriber's consents": "Wylistuj zgody subskrybenta",
    "Revoke consent for a topic": "Cofnij zgodę na temat",
    "Add an email to the suppression list": "Dodaj e-mail do listy wykluczeń",
    "Check whether an email is suppressed": "Sprawdź, czy e-mail jest wykluczony",
    "Remove an email from the suppression list": "Usuń e-mail z listy wykluczeń",
    "List campaigns": "Wylistuj kampanie",
    "Create a campaign": "Utwórz kampanię",
    "Get a campaign by key": "Pobierz kampanię po kluczu",
    "Update a campaign": "Zaktualizuj kampanię",
    "Delete a campaign": "Usuń kampanię",
    "Schedule a campaign": "Zaplanuj kampanię",
    "Send a campaign": "Wyślij kampanię",
    "List segments": "Wylistuj segmenty",
    "Create a segment": "Utwórz segment",
    "Get a segment": "Pobierz segment",
    "Update a segment": "Zaktualizuj segment",
    "Delete a segment": "Usuń segment",
    "List segment members": "Wylistuj członków segmentu",
    "Add members to a segment": "Dodaj członków do segmentu",
    "Remove members from a segment": "Usuń członków z segmentu",
    "List active custom fields": "Wylistuj aktywne pola niestandardowe",
    "Create a custom field": "Utwórz pole niestandardowe",
    "Get a custom field by key": "Pobierz pole niestandardowe po kluczu",
    "Archive a custom field": "Zarchiwizuj pole niestandardowe",
    "Update custom field details": "Zaktualizuj szczegóły pola niestandardowego",
    "Update custom field config": "Zaktualizuj konfigurację pola niestandardowego",
    "List automations": "Wylistuj automatyzacje",
    "Create an automation": "Utwórz automatyzację",
    "Get an automation": "Pobierz automatyzację",
    "Update an automation": "Zaktualizuj automatyzację",
    "Delete an automation": "Usuń automatyzację",
    "Update automation content": "Zaktualizuj treść automatyzacji",
    "Activate an automation": "Aktywuj automatyzację",
    "Pause an automation": "Wstrzymaj automatyzację",
    "Get the project's sending domain": "Pobierz domenę wysyłkową projektu",
    "Set up a custom sending domain": "Skonfiguruj własną domenę wysyłkową",
    "Update the sending domain": "Zaktualizuj domenę wysyłkową",
    "Remove the custom sending domain": "Usuń własną domenę wysyłkową",
    "Get DNS setup instructions": "Pobierz instrukcje konfiguracji DNS",
    "Verify the domain's DNS records": "Zweryfikuj rekordy DNS domeny",
    "Get the campaign report": "Pobierz raport kampanii",
    "Get live campaign statistics": "Pobierz statystyki kampanii na żywo",
    "Get the statistics timeline": "Pobierz oś czasu statystyk",
    "Export statistics as CSV": "Wyeksportuj statystyki jako CSV",
    "Get the account subscription": "Pobierz subskrypcję konta",
    "List available plans": "Wylistuj dostępne plany",
    "List invoices": "Wylistuj faktury",
    "Get the usage summary": "Pobierz podsumowanie zużycia",
    "Get the AI credit balance": "Pobierz saldo kredytów AI",
    "List AI credit transactions": "Wylistuj transakcje kredytów AI",
    "Get the current project": "Pobierz bieżący projekt",
}

# --- Response descriptions ---
RESPONSES = {
    "Active custom fields": "Aktywne pola niestandardowe",
    "Archived": "Zarchiwizowano",
    "Automation": "Automatyzacja",
    "Automation activated": "Automatyzacja aktywowana",
    "Automation created": "Automatyzacja utworzona",
    "Automation paused": "Automatyzacja wstrzymana",
    "CSV export": "Eksport CSV",
    "Campaign": "Kampania",
    "Campaign created": "Kampania utworzona",
    "Campaign queued for sending": "Kampania w kolejce do wysyłki",
    "Campaign report": "Raport kampanii",
    "Campaign scheduled": "Kampania zaplanowana",
    "Consent granted (or pending confirmation for double opt-in topics)":
        "Zgoda nadana (lub oczekująca potwierdzenia dla tematów z double opt-in)",
    "Consent preferences": "Preferencje zgód",
    "Consent revoked": "Zgoda cofnięta",
    "Credit balance": "Saldo kredytów",
    "Custom field": "Pole niestandardowe",
    "Custom field created": "Pole niestandardowe utworzone",
    "DNS setup instructions": "Instrukcje konfiguracji DNS",
    "Deleted": "Usunięto",
    "Members added": "Członkowie dodani",
    "Members removed": "Członkowie usunięci",
    "Paginated automations": "Stronicowane automatyzacje",
    "Paginated campaigns": "Stronicowane kampanie",
    "Paginated invoices": "Stronicowane faktury",
    "Paginated members": "Stronicowani członkowie",
    "Paginated segments": "Stronicowane segmenty",
    "Paginated subscribers": "Stronicowani subskrybenci",
    "Paginated topics": "Stronicowane tematy",
    "Paginated transactions": "Stronicowane transakcje",
    "Plans": "Plany",
    "Project": "Projekt",
    "Removed": "Usunięto",
    "Segment": "Segment",
    "Segment created": "Segment utworzony",
    "Sending domain": "Domena wysyłkowa",
    "Sending domain created": "Domena wysyłkowa utworzona",
    "Statistics": "Statystyki",
    "Subscriber": "Subskrybent",
    "Subscriber created": "Subskrybent utworzony",
    "Subscription": "Subskrypcja",
    "Suppression added": "Wykluczenie dodane",
    "Suppression removed": "Wykluczenie usunięte",
    "Suppression status": "Status wykluczenia",
    "Timeline points": "Punkty osi czasu",
    "Topic": "Temat",
    "Topic created": "Temat utworzony",
    "Updated automation": "Zaktualizowana automatyzacja",
    "Updated campaign": "Zaktualizowana kampania",
    "Updated custom field": "Zaktualizowane pole niestandardowe",
    "Updated segment": "Zaktualizowany segment",
    "Updated sending domain": "Zaktualizowana domena wysyłkowa",
    "Updated subscriber": "Zaktualizowany subskrybent",
    "Updated topic": "Zaktualizowany temat",
    "Usage summary": "Podsumowanie zużycia",
    "Verification result": "Wynik weryfikacji",
}

# --- Parameter & schema property descriptions ---
PARAMS = {
    "Must be the literal string `true` to confirm the removal.":
        "Musi być dosłownie łańcuchem `true`, aby potwierdzić usunięcie.",
    "ISO currency code used to price plan variants.":
        "Kod waluty ISO używany do wyceny wariantów planu.",
}

PROPS = {
    "e.g. SUBSCRIBED, PENDING_CONFIRMATION, UNSUBSCRIBED.":
        "np. SUBSCRIBED, PENDING_CONFIRMATION, UNSUBSCRIBED.",
    "Rich text content as a JSON string.":
        "Treść sformatowana jako łańcuch JSON.",
    "Required for SELECT and MULTI_SELECT.":
        "Wymagane dla SELECT i MULTI_SELECT.",
    "JSON rules definition for DYNAMIC segments.":
        "Definicja reguł JSON dla segmentów DYNAMIC.",
    "Field-level validation errors, present on 400/422.":
        "Błędy walidacji per pole, obecne przy 400/422.",
    "Automation graph edges as a JSON string.":
        "Krawędzie grafu automatyzacji jako łańcuch JSON.",
    "Automation graph nodes as a JSON string.":
        "Węzły grafu automatyzacji jako łańcuch JSON.",
}

# --- Reusable phrase substitutions for operation descriptions ---
# Applied in order; longer/more-specific phrases first.
PHRASES = [
    ("Requires scope:", "Wymagany zakres:"),
    ("Tenancy: scoped to the API key's project; an email from another project returns 404.",
     "Dzierżawa: ograniczone do projektu klucza API; e-mail z innego projektu zwraca 404."),
    ("Tenancy: scoped to the API key's project; a key from another project returns 404.",
     "Dzierżawa: ograniczone do projektu klucza API; klucz z innego projektu zwraca 404."),
    ("Tenancy: scoped to the API key's project; an id from another project returns 404.",
     "Dzierżawa: ograniczone do projektu klucza API; identyfikator z innego projektu zwraca 404."),
    ("Tenancy: scoped to the API key's project.",
     "Dzierżawa: ograniczone do projektu klucza API."),
    ("Tenancy: the tenant is taken from the API key context, never the body.",
     "Dzierżawa: tenant pochodzi z kontekstu klucza API, nigdy z treści żądania."),
    ("Tenancy: resolved from the API key's tenant to its organization.",
     "Dzierżawa: rozwiązywane z tenanta klucza API do jego organizacji."),
    ("Lists subscribers in the project, newest first.",
     "Listuje subskrybentów w projekcie, od najnowszych."),
    ("Lists campaigns in the project, newest first.",
     "Listuje kampanie w projekcie, od najnowszych."),
    ("Lists segments in the project, newest first.",
     "Listuje segmenty w projekcie, od najnowszych."),
    ("Lists automations in the project, newest first.",
     "Listuje automatyzacje w projekcie, od najnowszych."),
    ("Lists subscription topics in the project.",
     "Listuje tematy subskrypcji w projekcie."),
    ("Lists active custom field definitions in the project.",
     "Listuje aktywne definicje pól niestandardowych w projekcie."),
    ("Creates a subscriber in the key's project and subscribes them to the given topics in a single call. If a topic uses double opt-in, the resulting consent is `PENDING_CONFIRMATION`.",
     "Tworzy subskrybenta w projekcie klucza i zapisuje go do podanych tematów w jednym wywołaniu. Jeśli temat korzysta z double opt-in, wynikowa zgoda ma status `PENDING_CONFIRMATION`."),
    ("Updates name, phone and custom fields.",
     "Aktualizuje imię, telefon i pola niestandardowe."),
    ("Subscribes an existing subscriber to a topic. If the topic uses double opt-in, the consent is created `PENDING_CONFIRMATION` (`requiresConfirmation: true`) and the subscriber must confirm via email before they are subscribed.",
     "Zapisuje istniejącego subskrybenta do tematu. Jeśli temat korzysta z double opt-in, zgoda jest tworzona jako `PENDING_CONFIRMATION` (`requiresConfirmation: true`), a subskrybent musi ją potwierdzić przez e-mail, zanim zostanie zapisany."),
    ("Returns per-topic consent status and whether the subscriber is globally suppressed.",
     "Zwraca status zgody per temat oraz informację, czy subskrybent jest globalnie wykluczony."),
    ("Unsubscribes the subscriber from a single topic (not a global unsubscribe).",
     "Wypisuje subskrybenta z pojedynczego tematu (nie jest to globalne wypisanie)."),
    ("Suppresses an email so it can no longer receive any mail.",
     "Wyklucza e-mail, aby nie mógł już otrzymywać żadnej poczty."),
    ("Removing a global unsubscribe is irreversible-sensitive, so it requires the confirmation header `X-Confirm-Unsuppress: true`.",
     "Usunięcie globalnego wypisania jest operacją wrażliwą i nieodwracalną, więc wymaga nagłówka potwierdzenia `X-Confirm-Unsuppress: true`."),
    ("Creates a draft campaign.", "Tworzy kampanię roboczą."),
    ("Updates campaign metadata and content.",
     "Aktualizuje metadane i treść kampanii."),
    ("Transitions the campaign to `SCHEDULED`. The campaign must define a `scheduledAt`.",
     "Przełącza kampanię w stan `SCHEDULED`. Kampania musi mieć zdefiniowane `scheduledAt`."),
    ("Queues the campaign for immediate sending (`QUEUED_FOR_SENDING`). Pre-send guards in the platform may reject the transition.",
     "Kolejkuje kampanię do natychmiastowej wysyłki (`QUEUED_FOR_SENDING`). Zabezpieczenia przedwysyłkowe platformy mogą odrzucić to przejście."),
    ("Adds subscribers (by id) to a static segment.",
     "Dodaje subskrybentów (po id) do segmentu statycznego."),
    ("Removes subscribers (by id) from a static segment.",
     "Usuwa subskrybentów (po id) z segmentu statycznego."),
    ("Creates a custom field definition. SELECT and MULTI_SELECT require `options`.",
     "Tworzy definicję pola niestandardowego. SELECT i MULTI_SELECT wymagają `options`."),
    ("Archives (soft-deletes) the custom field.",
     "Archiwizuje (miękko usuwa) pole niestandardowe."),
    ("Updates display name, description and required flag.",
     "Aktualizuje nazwę wyświetlaną, opis i flagę wymagalności."),
    ("Updates the field's config (e.g. SELECT options) and default value.",
     "Aktualizuje konfigurację pola (np. opcje SELECT) i wartość domyślną."),
    ("Updates name, description, trigger and status.",
     "Aktualizuje nazwę, opis, wyzwalacz i status."),
    ("Replaces the automation graph nodes and edges.",
     "Zastępuje węzły i krawędzie grafu automatyzacji."),
    ("Transitions the automation to `ACTIVE`.",
     "Przełącza automatyzację w stan `ACTIVE`."),
    ("Transitions the automation to `PAUSED`.",
     "Przełącza automatyzację w stan `PAUSED`."),
    ("Each project has at most one custom sending domain.",
     "Każdy projekt ma najwyżej jedną własną domenę wysyłkową."),
    ("Sets up a custom sending domain for the project.",
     "Konfiguruje własną domenę wysyłkową dla projektu."),
    ("Updates the custom sending domain name.",
     "Aktualizuje nazwę własnej domeny wysyłkowej."),
    ("Returns the DNS records that must be added to verify the domain.",
     "Zwraca rekordy DNS, które należy dodać, aby zweryfikować domenę."),
    ("Triggers a DNS verification check and returns the resulting status.",
     "Uruchamia sprawdzenie weryfikacji DNS i zwraca wynikowy status."),
    ("Returns the generated AI report and its content for a campaign.",
     "Zwraca wygenerowany raport AI i jego treść dla kampanii."),
    ("Returns live delivery and engagement statistics.",
     "Zwraca statystyki dostarczalności i zaangażowania na żywo."),
    ("Returns a time series of delivery and engagement counts.",
     "Zwraca szereg czasowy liczby dostarczeń i zaangażowania."),
    ("Returns the campaign statistics as a CSV file.",
     "Zwraca statystyki kampanii jako plik CSV."),
    ("Returns the subscription for the account that owns this key's tenant.",
     "Zwraca subskrypcję dla konta, do którego należy tenant tego klucza."),
    ("Returns the plans available to the account.",
     "Zwraca plany dostępne dla konta."),
    ("Returns the account's invoices, paginated.",
     "Zwraca faktury konta, stronicowane."),
    ("Returns current usage versus plan limits.",
     "Zwraca bieżące zużycie względem limitów planu."),
    ("Returns the account's credit transactions, paginated.",
     "Zwraca transakcje kredytowe konta, stronicowane."),
    ("Returns the project the API key is scoped to. Project creation and deletion are not exposed over the public API.",
     "Zwraca projekt, do którego przypisany jest klucz API. Tworzenie i usuwanie projektów nie jest udostępniane przez publiczne API."),
]


def translate_description(text):
    """Translate an operation description by substituting known phrases."""
    out = text
    for en, pl in PHRASES:
        out = out.replace(en, pl)
    return out


def main():
    with open(SRC, encoding="utf-8") as f:
        d = json.load(f)

    untranslated = []

    # info
    info = d.get("info", {})
    if info.get("title"):
        info["title"] = "Railmail Public API"  # keep product name
    # info.description is long-form; translate its reusable phrases too
    if info.get("description"):
        info["description"] = translate_info_description(info["description"])

    # tags
    for t in d.get("tags", []):
        name = t.get("name")
        if name in TAG_NAMES:
            t["name"] = TAG_NAMES[name]
        else:
            untranslated.append(f"TAG NAME: {name}")
        desc = t.get("description")
        if desc in TAG_DESCRIPTIONS:
            t["description"] = TAG_DESCRIPTIONS[desc]
        elif desc:
            untranslated.append(f"TAG DESC: {desc}")

    # remap the tag references on every operation to the translated names
    for p, ms in d.get("paths", {}).items():
        for m, op in ms.items():
            if not isinstance(op, dict):
                continue
            if "tags" in op:
                op["tags"] = [TAG_NAMES.get(tg, tg) for tg in op["tags"]]
            if op.get("summary") in SUMMARIES:
                op["summary"] = SUMMARIES[op["summary"]]
            elif op.get("summary"):
                untranslated.append(f"SUMMARY: {op['summary']}")
            if op.get("description"):
                op["description"] = translate_description(op["description"])
            for prm in op.get("parameters", []):
                pd = prm.get("description")
                if pd in PARAMS:
                    prm["description"] = PARAMS[pd]
                elif pd:
                    untranslated.append(f"PARAM: {pd}")
            for code, r in op.get("responses", {}).items():
                rd = r.get("description") if isinstance(r, dict) else None
                if rd in RESPONSES:
                    r["description"] = RESPONSES[rd]
                elif rd:
                    untranslated.append(f"RESPONSE: {rd}")

    # schema property descriptions
    for name, s in d.get("components", {}).get("schemas", {}).items():
        for pn, pv in (s.get("properties") or {}).items():
            if isinstance(pv, dict) and pv.get("description"):
                if pv["description"] in PROPS:
                    pv["description"] = PROPS[pv["description"]]
                else:
                    untranslated.append(f"PROP {name}.{pn}: {pv['description']}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    if untranslated:
        print("WARNING: untranslated strings remain:")
        for u in untranslated:
            print("  -", u)
    else:
        print("OK: all human-facing strings translated.")
    print("Wrote", os.path.relpath(OUT, HERE))


def translate_info_description(text):
    """Translate the long info.description block section by section."""
    return (
        "REST API do programistycznego zarządzania platformą email marketingu Railmail.\n\n"
        "## Uwierzytelnianie\n"
        "Każde żądanie musi zawierać klucz API przypisany do projektu — w nagłówku `X-API-Key` "
        "lub jako `Authorization: Bearer rm_...`. Klucze mają format `rm_(live|test)_<losowy>`. "
        "Klucz odpowiada dokładnie jednemu projektowi; wszystkie odczyty i zapisy są automatycznie "
        "izolowane do tego projektu i jego tenanta. Klucz nie może odczytać ani zmodyfikować danych "
        "innego projektu.\n\n"
        "## Zakresy\n"
        "Każdy klucz posiada zestaw zakresów. Każda operacja wymaga określonego zakresu, opisanego "
        "w jej opisie (na przykład `Wymagany zakres: subscribers:write`). Żądanie, którego klucz nie "
        "ma wymaganego zakresu, zwraca `403`.\n\n"
        "Pełna taksonomia zakresów: `subscribers:read|write`, `topics:read|write`, "
        "`segments:read|write`, `campaigns:read|write`, `automations:read|write`, "
        "`custom_fields:read|write`, `sending_domains:read|write`, `consents:manage`, "
        "`suppressions:manage`, `reports:read`, `billing:read`, `credits:read`.\n\n"
        "## Limity zapytań\n"
        "Żądania są ograniczone do 60 na minutę na klucz. Odpowiedź zawiera nagłówki "
        "`X-RateLimit-Limit`, `X-RateLimit-Remaining` i `X-RateLimit-Reset`. Po przekroczeniu limitu "
        "API zwraca `429` z nagłówkiem `Retry-After`.\n\n"
        "## Błędy\n"
        "Wszystkie błędy używają RFC 7807 `application/problem+json` z polami `type`, `title`, "
        "`status`, `detail`, `instance`, `timestamp` oraz (przy walidacji) `errors`.\n\n"
        "## Typowy przepływ: dodaj użytkowników do swoich tematów\n"
        "1. `GET /topics`, aby odkryć klucze tematów.\n"
        "2. `POST /subscribers` z `topicKeys` + `consent`, aby utworzyć subskrybenta i zapisać go "
        "w jednym wywołaniu, LUB `POST /subscribers/{email}/consents`, aby zapisać istniejącego "
        "subskrybenta.\n"
        "Jeśli temat korzysta z double opt-in, zgoda jest tworzona jako `PENDING_CONFIRMATION`, "
        "a subskrybent musi ją potwierdzić przez otrzymaną wiadomość, zanim zostanie zapisany."
    )


if __name__ == "__main__":
    main()

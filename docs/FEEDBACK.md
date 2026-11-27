# Internship Feedback & Reflections

**English** · [한국어](FEEDBACK.ko.md) · [Portfolio README](../README.md)

These examples come from my internship feedback notes and personal reflections. I have summarized the reviews in my own words and linked the implementation and tests in the internship baseline.

| Case | What changed in the code | What I took from it |
| --- | --- | --- |
| [Number Baseball · Test more than scoring](#number-baseball--test-more-than-scoring) | Split validation from console input and tested invalid guesses | Start with a failing test and give reviewers changes they can follow |
| [Kiosk · Follow the whole order](#kiosk--follow-the-whole-order) | Included option recipes in stock requirements and tested checkout | Use an acceptance scenario to find missing rules before modeling them |
| [Kiosk · Design the API around checkout](#kiosk--design-the-api-around-checkout) | Built a cart per order request and accepted option IDs | Explain which state the API owns and trace where its data comes from |
| [Kiosk · Know what a lock protects](#kiosk--know-what-a-lock-protects) | Coordinated stock updates with transaction-level locks | Explain the lock scope and verify competing transactions on PostgreSQL |
| [Migration · Preserve the upgrade path](#migration--preserve-the-upgrade-path) | The baseline contains a linked Alembic revision chain | Test upgrades from an existing schema as well as fresh setup |

## Number Baseball · Test More Than Scoring

**Review focus.** The assignment called for handling invalid input and keeping console I/O separate from the game rules. I also received pull request feedback on my second iteration and used it to guide the next refactor.

**What I was thinking.** I had started with `main()` and the output for a correct guess, as I would for an algorithm exercise. I realized I also needed to define what happens when a player enters a letter or repeats a digit. Reviewing my changes made me think about how much a teammate could reasonably read in one commit.

**What I changed.** I extracted `InputValidator` from `ConsoleIO`. The test suite covers noninteger input, invalid lengths and ranges, duplicate digits, scoring, and the seven-attempt limit. [Validation refactor](https://github.com/jisung1017/internship/commit/e3a17a2) · [Number Baseball tests](../assignments_1/test_baseball.py)

**What I would do next.** Start each behavior with one failing test. After checking the change, make a focused commit whose message explains the intent.

## Kiosk · Follow the Whole Order

**Feedback.** The first kiosk review asked me to spend less effort checking simple assignments and more on boundary cases and checkout behavior, especially payment and stock deduction.

**What I was thinking.** I designed individual objects and wrote small tests before walking through an entire order. After the CLI took shape, I realized that an extra espresso shot also consumes beans. Adding that rule meant revisiting both the model and its tests. My notes identify an acceptance scenario as the place I would start next time.

**What I changed.** An order line now collects the recipe for the drink and the recipes for its selected options. In the CLI acceptance tests, the plain drink uses 18 units of beans, and adding two shots raises the total to 38. A separate test checks that a stock shortage leaves the inventory quantity unchanged. [Order-line recipes](../assignments_2/src/domain/cart_item.py) · [Checkout acceptance tests](../assignments_2/tests/test_acceptance.py)

**What I would do next.** Write the checkout scenario first, then list the relevant minimum and maximum inputs, values just outside those bounds, and cases such as zero or empty selections.

## Kiosk · Design the API Around Checkout

**Feedback.** The August 4 review asked who should own cart state between requests. On August 6, the review exposed how hard it was to follow the ORM data flow or construct a request from the Swagger docs. The August 10 feedback returned to the client journey and raised option IDs and menu filtering.

**What I was thinking.** I had largely put the CLI workflow behind HTTP. I could see responses in Swagger, but I struggled to explain where the response data came from or how someone else would know what to send. Walking through a customer's order helped me identify what the client should submit at checkout.

**What I changed.** The order service builds a fresh cart from the items in each submitted order. Clients can send numeric option IDs, and the menu endpoint supports category and tag filters with availability. The request schema includes an order example, and API tests check the order UUID and `Location` header. [Order service](../assignments_2/src/application/order_application_service.py) · [Kiosk routes](../assignments_2/src/interface/api/routers/kiosk.py) · [API schemas](../assignments_2/src/interface/api/schemas.py) · [Order API tests](../assignments_2/tests/test_kiosk_order_api.py)

**What I would do next.** Walk a reviewer through one complete request, from the payload through the service and ORM to the response. The API tests use test doubles. Verifying that flow against PostgreSQL remains a separate task.

## Kiosk · Know What a Lock Protects

**Feedback.** During the August 10 review, I had used `with_for_update()` for concurrent ordering and was asked to explain what it protected and why the ordering flow needed it.

**What I was thinking.** I could get orders through one at a time. I still needed to understand what happens when an order, a restock, or a cancellation touches the same ingredient during another transaction.

**What I changed.** The baseline acquires PostgreSQL transaction-level advisory locks in ascending ingredient ID order before reading stock. Stock writes follow that lock scope. The order status update path also uses a row lock on the order. The PostgreSQL test suite contains order, restock, and cancellation scenarios with concurrent requests. [Inventory lock implementation](../assignments_2/src/infrastructure/repositories/orm_inventory_repository.py) · [Order repository](../assignments_2/src/infrastructure/repositories/orm_order_repository.py) · [Concurrency scenarios](../assignments_2/tests/test_concurrency.py)

**What remains.** The lock protocol depends on writers using it consistently. The PostgreSQL concurrency tests were deferred during portfolio preparation, so verification against a disposable database remains open.

## Migration · Preserve the Upgrade Path

**My troubleshooting note.** When an earlier Alembic revision caused trouble locally, I replaced it and stamped my local database. A database that still referenced the earlier revision could no longer follow the upgrade path. Working on my machine had hidden the problem facing an existing checkout.

**What the baseline shows.** The checked-in Alembic revisions reference one another through `down_revision`. The portfolio review did not verify that databases on the replaced revision can upgrade to the current schema. [Revision chain](../assignments_2/migrations/versions/) · [Migration caveats](../assignments_2/README.md#getting-started)

**What I would do next.** Preserve revisions other developers may already have applied. Verify both a fresh installation and an upgrade from an older database with representative data.

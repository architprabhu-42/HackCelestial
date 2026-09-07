# Golden outputs

The Gate A2 planner goldens were added to lock the Document 04 hero arithmetic, result buckets, Pareto frontier and three deterministic ranking orders. They are generated only from `mumbai-goa-v2` through the production fixture loader, D1 event application, atomic traversal and shared evaluator.

Regenerate proposed outputs with `python -m resilitrip.tools.export_planner_goldens` into a temporary directory and review the diff before replacing these accepted files.

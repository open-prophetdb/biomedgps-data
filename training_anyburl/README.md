> We employ the AnyBURL framework to train a rule-based model for knowledge graph completion. It learns rules from the knowledge graph. The rules are then used to predict missing triples and explain prediction triples in the knowledge graph. The AnyBURL framework is available at `https://web.informatik.uni-mannheim.de/AnyBURL/`.

## Environment

Java 11

## Prepare Training/Validation/Test Data

See the README.md in the `training_kge` directory.

## Training

More details can be found in the `https://web.informatik.uni-mannheim.de/AnyBURL/` website.

```
java -Xmx12G -cp AnyBURL-23-1-1.jar de.unima.ki.anyburl.LearnReinforced training-config.properties
```

## Prediction

```
java -Xmx12G -cp AnyBURL-23-1-1.jar de.unima.ki.anyburl.Apply prediction-config.properties
```

## Evaluation

```
java -Xmx12G -cp AnyBURL-23-1-1.jar de.unima.ki.anyburl.Eval evaluation-config.properties
```

## Explain Prediction

We applied AnyBURL also to explain predictions. These predictions might have been made by AnyBURL or any other knowledge graph completion technique. The input required is a set of triples that you want to explain listed in a file called target.txt. Suppose for example that a model predicted 01062739 as tail of the query 00789448 _verb_group ? \(example taken from WN18RR. Than you add 00789448 _verb_group 01062739 to your target.txt file.

The folder of the target.txt file is the first argument. The explanation and temporary results (e.g., the rule file) are stored in that folder. The folder to the dataset is the second argument. It is assumed that the relevant files in that folder are the files train.txt, valid.txt, and test.txt. You call the explanation code as follows:

```
java -Xmx3G -cp AnyBURL-22.jar de.unima.ki.anyburl.Explain explanations/ data/<dataset_name>/
```
"""使用 VGG16 对 data/<汉字>/*.png 数据集进行迁移学习。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import tensorflow as tf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("Ret_Model"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--weights", choices=("imagenet", "none"), default="imagenet")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    classes = sorted(p.name for p in args.data.iterdir() if p.is_dir())
    if len(classes) < 2:
        raise SystemExit(f"训练至少需要 2 个汉字类别；在 {args.data} 找到 {len(classes)} 个。")
    tf.keras.utils.set_random_seed(args.seed)
    image_size = (args.image_size, args.image_size)
    generator = tf.keras.preprocessing.image.ImageDataGenerator(
        validation_split=0.2,
    )
    common = dict(
        directory=str(args.data), target_size=image_size, color_mode="rgb",
        batch_size=args.batch_size, class_mode="categorical", seed=args.seed,
    )
    train = generator.flow_from_directory(subset="training", shuffle=True, **common)
    validation = generator.flow_from_directory(subset="validation", shuffle=False, **common)
    if train.samples == 0 or validation.samples == 0:
        raise SystemExit("训练/验证集为空；每个汉字类别至少需要 2 张字体图片。")

    weights = "imagenet" if args.weights == "imagenet" else None
    base = tf.keras.applications.VGG16(
        include_top=False, weights=weights, input_shape=(*image_size, 3)
    )
    base.trainable = False
    inputs = tf.keras.Input(shape=(*image_size, 3))
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomRotation(0.03),
            tf.keras.layers.RandomTranslation(0.05, 0.05),
            tf.keras.layers.RandomZoom(0.1),
        ],
        name="data_augmentation",
    )
    x = augmentation(inputs)
    x = tf.keras.applications.vgg16.preprocess_input(x)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(train.num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy", metrics=["accuracy"],
    )

    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "class_indices.json").open("w", encoding="utf-8") as stream:
        json.dump(train.class_indices, stream, ensure_ascii=False, indent=2)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(args.output / "best.keras", monitor="val_loss", save_best_only=True),
    ]
    model.fit(train, validation_data=validation, epochs=args.epochs, callbacks=callbacks)
    model.save(args.output / "seal_character_vgg16.keras")
    print(f"模型和类别映射已保存到 {args.output.resolve()}")


if __name__ == "__main__":
    main()

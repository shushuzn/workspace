"""
TinySpeak CLI - Command Line Interface
"""
import click
import asyncio
import sys
from pathlib import Path
from tinyspeak import TTSEngine


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """TinySpeak - Lightweight Local-First TTS Tool"""
    pass


@cli.command()
@click.argument("text")
@click.option("-v", "--voice", default="zh-CN-XiaoxiaoNeural", help="Voice name")
@click.option("-o", "--output", default=None, help="Output file path")
@click.option("-r", "--rate", default="+0%", help="Speaking rate (e.g., +10%, -20%)")
@click.option("-p", "--pitch", default="+0Hz", help="Pitch adjustment (e.g., +5Hz, -10Hz)")
@click.option("--volume", default="+0%", help="Volume adjustment (e.g., +10%, -20%)")
def speak(text, voice, output, rate, pitch, volume):
    """Convert text to speech"""
    engine = TTSEngine()

    click.echo(f"Generating speech...")
    click.echo(f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}")
    click.echo(f"  Voice: {voice}")

    try:
        audio_file = engine.synthesize_sync(
            text=text,
            voice=voice,
            output_file=output,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        click.echo(f"✅ Saved to: {audio_file}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("-l", "--locale", default=None, help="Filter by locale (e.g., zh-CN, en-US)")
@click.option("-g", "--gender", default=None, help="Filter by gender (Male, Female)")
def voices(locale, gender):
    """List available voices"""
    engine = TTSEngine()

    async def _list():
        all_voices = await engine.list_voices(locale)

        if gender:
            all_voices = [v for v in all_voices if v.gender.lower() == gender.lower()]

        return all_voices

    voice_list = asyncio.run(_list())

    click.echo(f"Found {len(voice_list)} voices:\n")

    # Show first 20
    for v in voice_list[:20]:
        click.echo(f"  {v.short_name:20} | {v.gender:6} | {v.locale}")

    if len(voice_list) > 20:
        click.echo(f"\n  ... and {len(voice_list) - 20} more. Use --locale to filter.")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-v", "--voice", default="zh-CN-XiaoxiaoNeural", help="Voice name")
@click.option("-o", "--output-dir", default="output", help="Output directory")
def batch(input_file, voice, output_dir):
    """Batch convert text file to speech"""
    input_path = Path(input_file)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    engine = TTSEngine()

    click.echo(f"Processing {len(lines)} lines...")

    for i, line in enumerate(lines, 1):
        output_file = f"line_{i:03d}.mp3"
        try:
            engine.synthesize_sync(
                text=line,
                voice=voice,
                output_file=str(output_path / output_file)
            )
            click.echo(f"  [{i}/{len(lines)}] ✅")
        except Exception as e:
            click.echo(f"  [{i}/{len(lines)}] ❌ {e}")

    click.echo(f"\n✅ Done! Output in: {output_path}")


if __name__ == "__main__":
    cli()
Shader "Hidden/Ominous/Video Post"
{
    // Una sola pasada con el tratamiento de una cámara doméstica antigua:
    // óptica imperfecta, imagen algo blanda, ruido fino y color apagado.
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Name "VideoPost"
            ZTest Always ZWrite Off Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            float4 _Video_Optics;  // x: distorsión, y: aberración, z: suavizado, w: viñeta
            float4 _Video_Signal;  // x: ruido, y: exposición, z: tiempo, w: imperfección momentánea
            float4 _Video_Grade;   // x: negros levantados, y: blancos, z: saturación, w: contraste
            float4 _Video_ShadowTint;
            float4 _Video_LightTint;
            float4 _Video_Detail;
            float4 _Video_Psx;     // x: niveles de color por canal, y: tramado  // x: aspecto pintado, y: afilado

            half3 Tap(float2 uv) { return SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv).rgb; }

            // Kuwahara de cuatro cuadrantes: se queda con la zona más uniforme. Da el aspecto algo
            // pintado de las texturas reescaladas, sin emborronar los bordes.
            half3 Painterly(float2 uv, float2 t)
            {
                half3 best = 0; half bestVar = 1e5;
                [unroll] for (int q = 0; q < 4; q++)
                {
                    float2 dir = float2(q % 2 == 0 ? -1 : 1, q < 2 ? -1 : 1);
                    half3 sum = 0, sum2 = 0;
                    [unroll] for (int y = 0; y < 2; y++)
                    [unroll] for (int x = 0; x < 2; x++)
                    {
                        half3 c = Tap(uv + float2(x + 0.5, y + 0.5) * dir * t);
                        sum += c; sum2 += c * c;
                    }
                    half3 mean = sum * 0.25;
                    half3 v = sum2 * 0.25 - mean * mean;
                    half var = v.r + v.g + v.b;
                    if (var < bestVar) { bestVar = var; best = mean; }
                }
                return best;
            }

            float Hash(float2 p)
            {
                float3 q = frac(float3(p.xyx) * 0.1031);
                q += dot(q, q.yzx + 33.33);
                return frac((q.x + q.y) * q.z);
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float2 d = i.texcoord - 0.5;
                float r2 = dot(d, d);
                // Lente: ligero barril, escalado para que no aparezcan bordes vacíos.
                float k = _Video_Optics.x;
                float2 uv = 0.5 + d * (1.0 - k * 0.5 + k * r2);

                float2 texel = _BlitTexture_TexelSize.xy * (_Video_Optics.z + _Video_Signal.w * 0.6);
                float2 ca = (uv - 0.5) * r2 * _Video_Optics.y;
                half3 c;
                c.r = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + ca).r;
                c.b = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv - ca).b;
                half g = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv).g * 0.4;
                g += SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + float2(texel.x, 0)).g * 0.15;
                g += SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv - float2(texel.x, 0)).g * 0.15;
                g += SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + float2(0, texel.y)).g * 0.15;
                g += SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv - float2(0, texel.y)).g * 0.15;
                c.g = g;
                // El rojo y el azul se difuminan más que el verde, como en los sensores baratos.
                c.r = lerp(c.r, SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + ca + float2(texel.x * 1.5, 0)).r, 0.35);
                c.b = lerp(c.b, SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv - ca - float2(texel.x * 1.5, 0)).b, 0.35);

                // Aspecto pintado y afilado fuerte, como un juego reescalado y grabado.
                float2 px = _BlitTexture_TexelSize.xy;
                c = lerp(c, Painterly(uv, px), _Video_Detail.x);
                half3 around = (Tap(uv + px * float2(1.5, 0)) + Tap(uv - px * float2(1.5, 0)) +
                                Tap(uv + px * float2(0, 1.5)) + Tap(uv - px * float2(0, 1.5))) * 0.25;
                half lumaC = dot(c, half3(0.299, 0.587, 0.114));
                half lumaA = dot(around, half3(0.299, 0.587, 0.114));
                c = max(0, c + (lumaC - lumaA) * _Video_Detail.y);

                #if !defined(UNITY_COLORSPACE_GAMMA)
                c = LinearToSRGB(c);
                #endif

                c *= _Video_Signal.y;
                // Etalonaje: contraste moderado, color apagado y dominante fría en sombras, cálida en luces.
                c = saturate((c - 0.35) * _Video_Grade.w + 0.35);
                float luma = dot(c, float3(0.299, 0.587, 0.114));
                c = lerp(luma.xxx, c, _Video_Grade.z);
                c *= lerp(_Video_ShadowTint.rgb, _Video_LightTint.rgb, smoothstep(0.08, 0.72, luma));
                c = _Video_Grade.x + c * (_Video_Grade.y - _Video_Grade.x);

                // Viñeta moderada.
                c *= 1.0 - _Video_Optics.w * smoothstep(0.1, 0.62, r2);

                // Ruido fino, algo más visible en las sombras, con un poco de color.
                float2 cell = floor(i.positionCS.xy);
                float t = frac(_Video_Signal.z) * 97.0;
                float n = Hash(cell + t) - 0.5;
                float2 nc = float2(Hash(cell * 1.7 + t + 11.0), Hash(cell * 2.3 + t + 23.0)) - 0.5;
                float amount = _Video_Signal.x * (1.0 + _Video_Signal.w) * lerp(1.5, 0.75, luma);
                c.r += (n + nc.x * 0.5) * amount;
                c.g += n * amount;
                c.b += (n + nc.y * 0.5) * amount;

                c = saturate(c);
                // Color de PlayStation: pocos niveles por canal con tramado ordenado 4 x 4.
                if (_Video_Psx.x > 1.5)
                {
                    const float bayer[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };
                    uint2 p = (uint2)floor(i.positionCS.xy) % 4;
                    float d = (bayer[p.y * 4 + p.x] / 16.0 - 0.5) * _Video_Psx.y;
                    float levels = _Video_Psx.x - 1.0;
                    c = floor(c * levels + 0.5 + d) / levels;
                    c = saturate(c);
                }
                #if !defined(UNITY_COLORSPACE_GAMMA)
                c = SRGBToLinear(c);
                #endif
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
